"""
Enhanced Coupon Model with Advanced Features

This module provides comprehensive coupon management with:
- Advanced validation logic
- Usage tracking per user
- Security constraints
- Statistics and reporting
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
import secrets


class CouponManager(models.Manager):
    """Custom manager for coupon operations"""
    
    def get_active_coupons(self):
        """Get all active coupons"""
        return self.filter(is_active=True)
    
    def get_valid_coupons(self):
        """Get coupons that are currently valid"""
        now = timezone.now()
        return self.filter(
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now
        )
    
    def get_coupon_by_code(self, code):
        """Get coupon by code (case insensitive)"""
        return self.filter(code__iexact=code).first()
    
    def get_user_coupons(self, user):
        """Get coupons used by specific user"""
        return self.filter(couponusage__user=user)


class Coupon(models.Model):
    """Enhanced Coupon Model with Advanced Features"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', _('percentage')),
        ('fixed', _('fixed')),
    ]
    
    # Basic Information
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name=_('Coupon Code'),
        help_text=_('Unique coupon code')
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Coupon Name'),
        help_text=_('Descriptive name for the coupon')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Coupon Description'),
        help_text=_('Detailed description and terms')
    )
    
    # Discount Configuration
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        verbose_name=_('Discount Type'),
        help_text=_('Discount type: percentage or fixed')
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Discount Value'),
        help_text=_('Discount value (percentage or amount)'),
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('100.00')),
            DecimalValidator(max_digits=10, decimal_places=2)
        ]
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Maximum Discount'),
        help_text=_('Maximum discount amount (for percentage only)'),
        validators=[
            MinValueValidator(Decimal('0.01')),
            DecimalValidator(max_digits=10, decimal_places=2)
        ]
    )
    
    # Usage Limits
    usage_limit = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Usage Limit'),
        help_text=_('Maximum number of times coupon can be used')
    )
    usage_limit_per_user = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Usage Limit Per User'),
        help_text=_('Number of times user can use coupon')
    )
    used_count = models.IntegerField(
        default=0,
        verbose_name=_('Usage Count'),
        help_text=_('Number of times coupon has been used')
    )
    
    # Order Requirements
    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Minimum Order Value'),
        help_text=_('Minimum order value to activate coupon'),
        validators=[
            MinValueValidator(Decimal('0.01')),
            DecimalValidator(max_digits=10, decimal_places=2)
        ]
    )
    max_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Maximum Order Value'),
        help_text=_('Maximum order value to apply coupon'),
        validators=[
            MinValueValidator(Decimal('0.01')),
            DecimalValidator(max_digits=10, decimal_places=2)
        ]
    )
    
    # Date Constraints
    valid_from = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Start Date'),
        help_text=_('Coupon validity start date')
    )
    valid_to = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('End Date'),
        help_text=_('Coupon validity end date')
    )
    
    # Status Control
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether the coupon is active and usable')
    )
    
    # Targeting (Optional)
    applicable_products = models.ManyToManyField(
        'Product',
        blank=True,
        verbose_name=_('Applicable Products'),
        help_text=_('Products this coupon can be applied to')
    )
    applicable_categories = models.ManyToManyField(
        'Category',
        blank=True,
        verbose_name=_('Applicable Categories'),
        help_text=_('Categories this coupon can be applied to')
    )
    
    # Audit Fields
    created_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_coupons',
        verbose_name=_('أنشئ بواسطة'),
        help_text=_('المستخدم الذي أنشأ الكوبون')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    objects = CouponManager()
    
    class Meta:
        db_table = 'api_coupon'
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        indexes = [
            models.Index(fields=['code'], name='coupon_code_idx'),
            models.Index(fields=['is_active'], name='coupon_active_idx'),
            models.Index(fields=['valid_from', 'valid_to'], name='coupon_dates_idx'),
            models.Index(fields=['used_count'], name='coupon_usage_idx'),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name or 'Untitled'}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure code is uppercase"""
        if self.code:
            self.code = self.code.upper().strip()
        super().save(*args, **kwargs)
    
    def is_valid(self, user=None, order_value=None):
        """Check if coupon is valid for use"""
        now = timezone.now()
        
        # Basic validity checks
        if not self.is_active:
            return False, _('الكوبون غير نشط')
        
        if self.valid_from and now < self.valid_from:
            return False, _('الكوبون لم يبدأ بعد')
        
        if self.valid_to and now > self.valid_to:
            return False, _('الكوبون انتهت صلاحيته')
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, _('تم الوصول إلى حد الاستخدام الأقصى')
        
        # Order value checks
        if order_value:
            if order_value < self.min_order_value:
                return False, _('الطلب لا يصل للحد الأدنى المطلوب')
            
            if self.max_order_value and order_value > self.max_order_value:
                return False, _('الطلب يتجاوز الحد الأقصى المسموح')
        
        # User-specific checks
        if user and user.is_authenticated:
            user_usage = self.get_user_usage_count(user)
            if user_usage >= self.usage_limit_per_user:
                return False, _('لقد استخدمت هذا الكوبون الحد الأقصى المسموح')
        
        return True, _('الكوبون صالح للاستخدام')
    
    def calculate_discount(self, order_value):
        """Calculate discount amount based on order value"""
        if self.discount_type == 'percentage':
            discount = (order_value * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        
        return max(discount, 0)
    
    def get_user_usage_count(self, user):
        """Get usage count for specific user"""
        if not user or not user.is_authenticated:
            return 0
        return CouponUsage.objects.filter(coupon=self, user=user).count()
    
    def increment_usage(self, user=None, order=None):
        """Increment usage count and create usage record"""
        self.used_count += 1
        self.save(update_fields=['used_count'])
        
        if user and user.is_authenticated:
            CouponUsage.objects.create(
                coupon=self,
                user=user,
                order=order,
                used_at=timezone.now()
            )
    
    @property
    def remaining_uses(self):
        """Get remaining uses"""
        if not self.usage_limit:
            return None  # Unlimited
        return max(0, self.usage_limit - self.used_count)
    
    @property
    def is_expired(self):
        """Check if coupon is expired"""
        now = timezone.now()
        return self.valid_to and now > self.valid_to
    
    @property
    def is_upcoming(self):
        """Check if coupon is not yet active"""
        now = timezone.now()
        return self.valid_from and now < self.valid_from
    
    def generate_code(self, length=8):
        """Generate random coupon code"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        while True:
            code = ''.join(secrets.choice(chars) for _ in range(length))
            if not Coupon.objects.filter(code=code).exists():
                return code


class CouponUsage(models.Model):
    """Track coupon usage per user and order"""
    
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name=_('الكوبون')
    )
    user = models.ForeignKey(
        'api.User',
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name=_('المستخدم')
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coupon_usages',
        verbose_name=_('الطلب')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('مبلغ الخصم'),
        validators=[
            MinValueValidator(Decimal('0.01')),
            DecimalValidator(max_digits=10, decimal_places=2)
        ]
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الاستخدام')
    )
    
    class Meta:
        db_table = 'api_coupon_usage'
        verbose_name = _('Coupon Usage')
        verbose_name_plural = _('Coupon Usages')
        unique_together = ['coupon', 'user', 'order']
        indexes = [
            models.Index(fields=['coupon', 'user'], name='coupon_usage_user_idx'),
            models.Index(fields=['used_at'], name='coupon_usage_date_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"


