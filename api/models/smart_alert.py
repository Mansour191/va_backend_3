"""
Smart Alert Model for VynilArt API
User-configurable alerts with custom conditions
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class SmartAlertManager(models.Manager):
    """Custom manager for smart alerts"""
    
    def active(self):
        """Get only active alerts"""
        return self.filter(is_active=True)
    
    def for_user(self, user):
        """Get alerts for specific user"""
        return self.filter(user=user)
    
    def active_for_user(self, user):
        """Get active alerts for specific user"""
        return self.filter(user=user, is_active=True)


class SmartAlert(models.Model):
    """Smart Alert model with user-defined conditions"""
    
    ALERT_TYPES = [
        ('PRICE_DROP', 'Price Drop'),
        ('STOCK_ALERT', 'Stock Alert'),
        ('NEW_PRODUCT', 'New Product'),
        ('ORDER_STATUS', 'Order Status'),
        ('PROMOTION', 'Promotion'),
        ('CUSTOM', 'Custom'),
    ]
    
    # Core fields matching api_alert table
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='smart_alerts'
    )
    type = models.CharField(
        max_length=50,
        choices=ALERT_TYPES,
        db_index=True
    )
    message = models.TextField(
        help_text="Alert message description"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this alert is enabled"
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom conditions for triggering this alert"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for enhanced functionality
    name = models.CharField(
        max_length=255,
        help_text="Custom name for this alert"
    )
    last_triggered = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this alert was last triggered"
    )
    trigger_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this alert has been triggered"
    )
    
    objects = SmartAlertManager()

    class Meta:
        db_table = 'api_smart_alert'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Smart Alert'
        verbose_name_plural = 'Smart Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or self.type} - {self.user.username}"

    @property
    def is_enabled(self):
        """Check if alert is enabled"""
        return self.is_active

    def enable(self):
        """Enable this alert"""
        if not self.is_active:
            self.is_active = True
            self.save()

    def disable(self):
        """Disable this alert"""
        if self.is_active:
            self.is_active = False
            self.save()

    def toggle_status(self):
        """Toggle alert status"""
        self.is_active = not self.is_active
        self.save()
        return self.is_active

    def trigger(self, save=True):
        """Mark alert as triggered"""
        self.last_triggered = timezone.now()
        self.trigger_count += 1
        if save:
            self.save()

    def get_condition_value(self, key, default=None):
        """Get a specific condition value"""
        return self.conditions.get(key, default)

    def set_condition(self, key, value, save=True):
        """Set a specific condition value"""
        if not self.conditions:
            self.conditions = {}
        self.conditions[key] = value
        if save:
            self.save()

    def check_conditions(self, context_data):
        """
        Check if alert conditions are met based on context data
        context_data: dict with relevant data for checking
        """
        if not self.is_active or not self.conditions:
            return False
        
        # Check based on alert type
        if self.type == 'PRICE_DROP':
            return self._check_price_drop_conditions(context_data)
        elif self.type == 'STOCK_ALERT':
            return self._check_stock_conditions(context_data)
        elif self.type == 'NEW_PRODUCT':
            return self._check_new_product_conditions(context_data)
        elif self.type == 'ORDER_STATUS':
            return self._check_order_status_conditions(context_data)
        elif self.type == 'PROMOTION':
            return self._check_promotion_conditions(context_data)
        elif self.type == 'CUSTOM':
            return self._check_custom_conditions(context_data)
        
        return False

    def _check_price_drop_conditions(self, context_data):
        """Check price drop conditions"""
        threshold = self.get_condition_value('threshold_percentage', 0)
        current_price = context_data.get('current_price', 0)
        old_price = context_data.get('old_price', 0)
        
        if old_price > 0:
            drop_percentage = ((old_price - current_price) / old_price) * 100
            return drop_percentage >= threshold
        return False

    def _check_stock_conditions(self, context_data):
        """Check stock conditions"""
        min_stock = self.get_condition_value('min_stock', 0)
        max_stock = self.get_condition_value('max_stock', None)
        current_stock = context_data.get('current_stock', 0)
        
        if max_stock is not None:
            return min_stock <= current_stock <= max_stock
        else:
            return current_stock <= min_stock

    def _check_new_product_conditions(self, context_data):
        """Check new product conditions"""
        categories = self.get_condition_value('categories', [])
        min_price = context_data.get('min_price', 0)
        max_price = context_data.get('max_price', None)
        
        product = context_data.get('product')
        if not product:
            return False
        
        # Check categories if specified
        if categories and product.category_id not in categories:
            return False
        
        # Check price range
        product_price = float(product.base_price)
        if product_price < min_price:
            return False
        if max_price is not None and product_price > max_price:
            return False
        
        return True

    def _check_order_status_conditions(self, context_data):
        """Check order status conditions"""
        target_statuses = self.get_condition_value('statuses', [])
        current_status = context_data.get('status', '')
        
        return current_status in target_statuses

    def _check_promotion_conditions(self, context_data):
        """Check promotion conditions"""
        min_discount = self.get_condition_value('min_discount', 0)
        categories = self.get_condition_value('categories', [])
        
        promotion = context_data.get('promotion')
        if not promotion:
            return False
        
        # Check discount percentage
        if promotion.discount_percent < min_discount:
            return False
        
        # Check categories if specified
        if categories:
            promotion_categories = promotion.applicable_categories.values_list('id', flat=True)
            return any(cat_id in promotion_categories for cat_id in categories)
        
        return True

    def _check_custom_conditions(self, context_data):
        """Check custom conditions - flexible implementation"""
        # This allows for complex custom conditions
        # Example conditions structure:
        # {
        #   "field": "price",
        #   "operator": "lte",
        #   "value": 1000,
        #   "and": [
        #     {
        #       "field": "category",
        #       "operator": "in",
        #       "value": [1, 2, 3]
        #     }
        #   ]
        # }
        
        def evaluate_condition(condition, data):
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field not in data:
                return False
            
            field_value = data[field]
            
            if operator == 'eq':
                return field_value == value
            elif operator == 'ne':
                return field_value != value
            elif operator == 'lt':
                return field_value < value
            elif operator == 'lte':
                return field_value <= value
            elif operator == 'gt':
                return field_value > value
            elif operator == 'gte':
                return field_value >= value
            elif operator == 'in':
                return field_value in value
            elif operator == 'not_in':
                return field_value not in value
            elif operator == 'contains':
                return value in str(field_value)
            elif operator == 'not_contains':
                return value not in str(field_value)
            
            return False
        
        # Evaluate main condition
        if not evaluate_condition(self.conditions, context_data):
            return False
        
        # Evaluate AND conditions if any
        and_conditions = self.conditions.get('and', [])
        for condition in and_conditions:
            if not evaluate_condition(condition, context_data):
                return False
        
        # Evaluate OR conditions if any
        or_conditions = self.conditions.get('or', [])
        if or_conditions:
            for condition in or_conditions:
                if evaluate_condition(condition, context_data):
                    return True
            return False
        
        return True

    def to_dict(self):
        """Convert alert to dictionary for API responses"""
        return {
            'id': self.id,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            },
            'name': self.name,
            'type': self.type,
            'type_display': self.get_type_display(),
            'message': self.message,
            'is_active': self.is_active,
            'is_enabled': self.is_enabled,
            'conditions': self.conditions,
            'created_at': self.created_at.isoformat(),
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count,
        }
