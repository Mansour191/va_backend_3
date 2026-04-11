"""
Enhanced Alert Models for VynilArt API
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from .product import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal
import json

# Removed get_user_model import and User assignment


class AlertManager(models.Manager):
    """Custom manager for alert items with enhanced query methods"""
    
    def active(self):
        """Get only active (unresolved) alerts"""
        return self.filter(is_resolved=False)
    
    def resolved(self):
        """Get only resolved alerts"""
        return self.filter(is_resolved=True)
    
    def low_stock(self):
        """Get low stock alerts"""
        return self.filter(alert_type='LOW_STOCK', is_resolved=False)
    
    def price_drop(self):
        """Get price drop alerts"""
        return self.filter(alert_type='PRICE_DROP', is_resolved=False)
    
    def back_in_stock(self):
        """Get back in stock alerts"""
        return self.filter(alert_type='BACK_IN_STOCK', is_resolved=False)
    
    def for_product(self, product):
        """Get alerts for specific product"""
        return self.filter(product=product)
    
    def urgent(self):
        """Get urgent alerts (critical stock levels, significant price drops)"""
        return self.filter(
            models.Q(alert_type='LOW_STOCK', threshold_value__lte=2) |
            models.Q(alert_type='PRICE_DROP', threshold_value__gte=Decimal('20.00'))
        ).filter(is_resolved=False)


class Alert(models.Model):
    """Enhanced Alert model for automated notifications"""
    
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('PRICE_DROP', 'Price Drop'),
        ('BACK_IN_STOCK', 'Back in Stock'),
        ('HIGH_DEMAND', 'High Demand'),
        ('PRICE_INCREASE', 'Price Increase'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    # Core fields
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        db_index=True
    )
    threshold_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Threshold value for triggering alert"
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Current value that triggered the alert"
    )
    
    # Status fields
    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether alert has been resolved by admin"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='MEDIUM',
        db_index=True
    )
    
    # Additional fields for enhanced functionality
    title = models.CharField(
        max_length=255,
        help_text="Alert title for display"
    )
    message = models.TextField(
        help_text="Detailed alert message"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional alert data (previous values, etc.)"
    )
    
    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When alert was marked as resolved"
    )
    resolved_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        help_text="Admin who resolved this alert"
    )
    
    # Notification settings
    auto_notify = models.BooleanField(
        default=True,
        help_text="Automatically send notifications for this alert"
    )
    notification_sent = models.BooleanField(
        default=False,
        help_text="Whether notification has been sent"
    )
    notification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When notification was sent"
    )
    
    objects = AlertManager()

    class Meta:
        indexes = [
            models.Index(fields=['product', 'alert_type', 'is_resolved']),
            models.Index(fields=['alert_type', 'is_resolved']),
            models.Index(fields=['priority', 'is_resolved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['notification_sent']),
        ]
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name_ar}"

    @property
    def is_critical(self):
        """Check if alert is critical"""
        return self.priority == 'CRITICAL'

    @property
    def is_urgent(self):
        """Check if alert is urgent"""
        return self.priority in ['HIGH', 'CRITICAL']

    @property
    def days_open(self):
        """Calculate days since alert was created"""
        if self.created_at:
            return (timezone.now() - self.created_at).days
        return 0

    @property
    def requires_immediate_attention(self):
        """Check if alert requires immediate attention"""
        return (
            self.is_critical or
            self.days_open > 7 or
            (self.alert_type == 'LOW_STOCK' and self.current_value <= 1)
        )

    def resolve(self, resolved_by_user=None):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if resolved_by_user:
            self.resolved_by = resolved_by_user
        self.save()

    def send_notification(self):
        """Send notification for this alert"""
        if not self.auto_notify or self.notification_sent:
            return False
        
        try:
            # Create notification
            from core.models import Notification
            
            # Determine notification recipients
            recipients = self.get_notification_recipients()
            
            for recipient in recipients:
                Notification.objects.create(
                    user=recipient,
                    title=self.title,
                    message=self.message,
                    notification_type='ALERT',
                    related_object_id=self.id,
                    related_object_type='alert',
                    metadata={
                        'alert_type': self.alert_type,
                        'product_id': self.product.id,
                        'product_name': self.product.name_ar,
                        'priority': self.priority,
                        'threshold_value': str(self.threshold_value),
                        'current_value': str(self.current_value),
                    }
                )
            
            self.notification_sent = True
            self.notification_sent_at = timezone.now()
            self.save()
            
            return True
            
        except Exception as e:
            print(f"Error sending notification for alert {self.id}: {e}")
            return False

    def get_notification_recipients(self):
        """Get list of users who should receive this alert"""
        recipients = []
        
        # Always notify admins for critical alerts
        if self.is_critical or self.is_urgent:
            recipients.extend(User.objects.filter(is_staff=True, is_active=True))
        
        # For price drops, notify users who have this product in wishlist
        if self.alert_type == 'PRICE_DROP':
            from api.models.wishlist import Wishlist
            wishlist_users = Wishlist.objects.filter(
                product=self.product,
                notify_on_discount=True
            ).values_list('user', flat=True)
            recipients.extend(User.objects.filter(id__in=wishlist_users, is_active=True))
        
        # For back in stock, notify users who have this product in wishlist
        if self.alert_type == 'BACK_IN_STOCK':
            from api.models.wishlist import Wishlist
            wishlist_users = Wishlist.objects.filter(
                product=self.product,
                notify_on_stock=True
            ).values_list('user', flat=True)
            recipients.extend(User.objects.filter(id__in=wishlist_users, is_active=True))
        
        # Remove duplicates
        return list(set(recipients))

    def generate_title_and_message(self):
        """Generate appropriate title and message based on alert type"""
        if self.alert_type == 'LOW_STOCK':
            self.title = f"مخزون منخفض: {self.product.name_ar}"
            self.message = (
                f"المخزون الحالي: {self.current_value} قطعة\n"
                f"الحد الأدنى: {self.threshold_value} قطعة\n"
                f"المنتج: {self.product.name_ar}\n"
                f"SKU: {self.product.sku if hasattr(self.product, 'sku') else 'N/A'}"
            )
            self.priority = 'HIGH' if self.current_value <= 2 else 'MEDIUM'
            
        elif self.alert_type == 'PRICE_DROP':
            self.title = f"انخفاض في السعر: {self.product.name_ar}"
            self.message = (
                f"انخفض سعر المنتج بنسبة {self.threshold_value}%\n"
                f"السعر القديم: {self.metadata.get('old_price', 'N/A')} د.ج\n"
                f"السعر الجديد: {self.current_value} د.ج\n"
                f"المنتج: {self.product.name_ar}"
            )
            self.priority = 'MEDIUM'
            
        elif self.alert_type == 'BACK_IN_STOCK':
            self.title = f"عاد للتوفر: {self.product.name_ar}"
            self.message = (
                f"المنتج الذي كنت تنتظره عاد للمخزون!\n"
                f"الكمية الحالية: {self.current_value} قطعة\n"
                f"المنتج: {self.product.name_ar}\n"
                f"السعر: {self.product.base_price} د.ج"
            )
            self.priority = 'HIGH'
            
        elif self.alert_type == 'OUT_OF_STOCK':
            self.title = f"نفد المخزون: {self.product.name_ar}"
            self.message = (
                f"لقد نفد هذا المنتج من المخزون\n"
                f"المنتج: {self.product.name_ar}\n"
                f"آخر كمية متاحة: {self.metadata.get('last_quantity', 'N/A')}"
            )
            self.priority = 'CRITICAL'
            
        elif self.alert_type == 'HIGH_DEMAND':
            self.title = f"طلب مرتفع: {self.product.name_ar}"
            self.message = (
                f"هذا المنتج يشهد طلباً مرتفعاً\n"
                f"المبيعات في 24 ساعة: {self.current_value}\n"
                f"المتوسط اليومي: {self.threshold_value}\n"
                f"المنتج: {self.product.name_ar}"
            )
            self.priority = 'MEDIUM'

    def to_dict(self):
        """Convert alert to dictionary for API responses"""
        return {
            'id': self.id,
            'product': {
                'id': self.product.id,
                'name_ar': self.product.name_ar,
                'name_en': self.product.name_en,
                'sku': getattr(self.product, 'sku', None),
                'base_price': float(self.product.base_price),
                'stock': self.product.stock,
            },
            'alert_type': self.alert_type,
            'alert_type_display': self.get_alert_type_display(),
            'threshold_value': float(self.threshold_value),
            'current_value': float(self.current_value),
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'priority_display': self.get_priority_display(),
            'is_resolved': self.is_resolved,
            'is_critical': self.is_critical,
            'is_urgent': self.is_urgent,
            'days_open': self.days_open,
            'requires_immediate_attention': self.requires_immediate_attention,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': {
                'id': self.resolved_by.id,
                'username': self.resolved_by.username
            } if self.resolved_by else None,
            'notification_sent': self.notification_sent,
            'notification_sent_at': self.notification_sent_at.isoformat() if self.notification_sent_at else None,
            'metadata': self.metadata,
        }


class AlertRule(models.Model):
    """Alert rules for automatic alert generation"""
    
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('PRICE_DROP', 'Price Drop'),
        ('HIGH_DEMAND', 'High Demand'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='alert_rules'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES
    )
    is_active = models.BooleanField(default=True)
    threshold_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Threshold value for triggering alert"
    )
    
    # Additional settings
    notify_admins = models.BooleanField(default=True)
    notify_customers = models.BooleanField(default=False)
    auto_resolve = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'alert_type']
        verbose_name = 'Alert Rule'
        verbose_name_plural = 'Alert Rules'

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name_ar}"

    def check_and_create_alert(self, current_value, metadata=None):
        """Check if alert should be created based on current value"""
        if not self.is_active:
            return None
        
        # Check if similar unresolved alert already exists
        existing_alert = Alert.objects.filter(
            product=self.product,
            alert_type=self.alert_type,
            is_resolved=False
        ).first()
        
        if existing_alert:
            return existing_alert
        
        # Create new alert if threshold is met
        should_create = False
        
        if self.alert_type == 'LOW_STOCK':
            should_create = current_value <= self.threshold_value
        elif self.alert_type == 'PRICE_DROP':
            should_create = current_value >= self.threshold_value
        elif self.alert_type == 'HIGH_DEMAND':
            should_create = current_value >= self.threshold_value
        
        if should_create:
            alert = Alert.objects.create(
                product=self.product,
                alert_type=self.alert_type,
                threshold_value=self.threshold_value,
                current_value=current_value,
                metadata=metadata or {},
                auto_notify=True
            )
            
            # Generate appropriate title and message
            alert.generate_title_and_message()
            alert.save()
            
            # Send notification if enabled
            if self.notify_admins or self.notify_customers:
                alert.send_notification()
            
            return alert
        
        return None


# Signal handlers for automatic alert generation
@receiver(pre_save, sender='api.Product')
def product_pre_save(sender, instance, **kwargs):
    """Check for price changes before saving product"""
    if not instance.pk:
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        old_price = old_instance.base_price
        new_price = instance.base_price
        
        if old_price != new_price:
            # Calculate price change percentage
            price_change_percent = abs((new_price - old_price) / old_price * 100)
            
            # Check for price drop alert rule
            from .alert import AlertRule
            price_drop_rule = AlertRule.objects.filter(
                product=instance,
                alert_type='PRICE_DROP',
                is_active=True
            ).first()
            
            if price_drop_rule and new_price < old_price:
                price_drop_rule.check_and_create_alert(
                    current_value=price_change_percent,
                    metadata={
                        'old_price': float(old_price),
                        'new_price': float(new_price),
                        'price_change': float(new_price - old_price)
                    }
                )
            
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender='api.Product')
def product_post_save(sender, instance, created, **kwargs):
    """Check for stock changes after saving product"""
    if created:
        return
    
    # Check for stock alerts
    from .alert import AlertRule
    stock_rule = AlertRule.objects.filter(
        product=instance,
        alert_type='LOW_STOCK',
        is_active=True
    ).first()
    
    if stock_rule:
        stock_rule.check_and_create_alert(
            current_value=instance.stock,
            metadata={'last_checked': timezone.now().isoformat()}
        )
