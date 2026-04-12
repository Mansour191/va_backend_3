"""
Coupon and Promotion Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class PromotionCoupon(models.Model):
    """
    Enhanced coupon system with comprehensive features
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('tiered', 'Tiered Discount'),
    ]
    
    # Basic information
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Discount configuration
    discount_type = models.CharField(
        max_length=20, 
        choices=DISCOUNT_TYPE_CHOICES, 
        default='percentage'
    )
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Usage limits
    usage_limit = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Total usage limit across all users"
    )
    usage_limit_per_user = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Usage limit per individual user"
    )
    used_count = models.IntegerField(default=0)
    
    # User restrictions
    min_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Minimum order amount to use coupon"
    )
    max_discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum discount amount for percentage coupons"
    )
    
    # Product and category restrictions
    applicable_products = models.JSONField(
        default=list,
        help_text="List of product IDs this coupon applies to"
    )
    excluded_products = models.JSONField(
        default=list,
        help_text="List of product IDs this coupon doesn't apply to"
    )
    applicable_categories = models.JSONField(
        default=list,
        help_text="List of category IDs this coupon applies to"
    )
    excluded_categories = models.JSONField(
        default=list,
        help_text="List of category IDs this coupon doesn't apply to"
    )
    
    # Geographic restrictions
    applicable_wilayas = models.JSONField(
        default=list,
        help_text="List of wilaya codes this coupon applies to"
    )
    
    # User segment restrictions
    applicable_user_segments = models.JSONField(
        default=list,
        help_text="List of user segment IDs this coupon applies to"
    )
    first_time_customers_only = models.BooleanField(default=False)
    
    # Time restrictions
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Advanced settings
    auto_apply = models.BooleanField(
        default=False,
        help_text="Automatically apply coupon if conditions are met"
    )
    stackable = models.BooleanField(
        default=False,
        help_text="Can be combined with other coupons"
    )
    
    # Buy X Get Y configuration
    buy_quantity = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Quantity to buy for Buy X Get Y offers"
    )
    get_quantity = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Quantity to get for Buy X Get Y offers"
    )
    get_product_id = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Product ID for Buy X Get Y offers"
    )
    
    # Tiered discount configuration
    tiers = models.JSONField(
        default=list,
        help_text="List of tiers for tiered discounts"
    )
    
    # Analytics and tracking
    times_used = models.IntegerField(default=0)
    total_discount_given = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Attribution
    created_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_promotion_coupons'
    )
    campaign = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from', 'valid_to']),
            models.Index(fields=['discount_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_to and now > self.valid_to:
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True

    @property
    def days_until_expiry(self):
        """Calculate days until coupon expires"""
        if not self.valid_to:
            return None
        
        delta = self.valid_to - timezone.now()
        return max(0, delta.days)

    def calculate_discount(self, order_amount, cart_items=None):
        """Calculate discount amount for given order"""
        if self.discount_type == 'percentage':
            discount = order_amount * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
        elif self.discount_type == 'fixed':
            discount = min(self.discount_value, order_amount)
        elif self.discount_type == 'free_shipping':
            discount = 0  # Would be calculated based on shipping
        elif self.discount_type == 'buy_x_get_y':
            discount = 0  # Would be calculated based on cart items
        elif self.discount_type == 'tiered':
            discount = 0  # Would be calculated based on order amount
        else:
            discount = 0
        
        return max(Decimal('0'), discount)


class PromotionCouponUsage(models.Model):
    """
    Track promotion coupon usage for analytics and fraud prevention
    """
    coupon = models.ForeignKey(
        PromotionCoupon, 
        on_delete=models.CASCADE, 
        related_name='usages'
    )
    user = models.ForeignKey(
        'api.User',
        on_delete=models.CASCADE,
        related_name='promotion_coupon_usages'
    )
    order = models.ForeignKey(
        'api.Order',
        on_delete=models.CASCADE,
        related_name='promotion_coupon_usages'
    )
    
    # Usage details
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_amount_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Context information
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamp
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_promotion_coupon_usage'
        indexes = [
            models.Index(fields=['coupon']),
            models.Index(fields=['user']),
            models.Index(fields=['order']),
            models.Index(fields=['used_at']),
        ]
        unique_together = ['coupon', 'user', 'order']

    def __str__(self):
        return f"{self.coupon.code} - {self.user.username}"


class CouponCampaign(models.Model):
    """
    Coupon campaigns for marketing analytics
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Campaign settings
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Targeting
    target_audience = models.JSONField(
        default=dict,
        help_text="Target audience criteria"
    )
    budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    
    # Performance tracking
    coupons_count = models.IntegerField(default=0)
    total_usage = models.IntegerField(default=0)
    total_discount_given = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Attribution
    created_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='coupon_campaigns'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_active_campaign(self):
        """Check if campaign is currently active"""
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date
        )
