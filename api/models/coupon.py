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
        ('percentage', _('نسبة مئوية')),
        ('fixed', _('مبلغ ثابت')),
    ]
    
    # Basic Information
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name=_('رمز الكوبون'),
        help_text=_('رمز فريد للكوبون')
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('اسم الكوبون'),
        help_text=_('اسم وصفي للكوبون')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف الكوبون'),
        help_text=_('وصف مفصل للكوبون وشروطه')
    )
    
    # Discount Configuration
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        verbose_name=_('نوع الخصم'),
        help_text=_('نوع الخصم: نسبة مئوية أو مبلغ ثابت')
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('قيمة الخصم'),
        help_text=_('قيمة الخصم (نسبة أو مبلغ)')
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('أقصى خصم'),
        help_text=_('أقصى قيمة للخصم (للنسب المئوية فقط)')
    )
    
    # Usage Limits
    usage_limit = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('حد الاستخدام'),
        help_text=_('الحد الأقصى لعدد مرات الاستخدام')
    )
    usage_limit_per_user = models.IntegerField(
        default=1,
        verbose_name=_('حد الاستخدام لكل مستخدم'),
        help_text=_('عدد المرات التي يمكن للمستخدم استخدام الكوبون')
    )
    used_count = models.IntegerField(
        default=0,
        verbose_name=_('مرات الاستخدام'),
        help_text=_('عدد المرات التي تم استخدام الكوبون')
    )
    
    # Order Requirements
    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('الحد الأدنى للطلب'),
        help_text=_('الحد الأدنى لقيمة الطلب لتفعيل الكوبون')
    )
    max_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('الحد الأقصى للطلب'),
        help_text=_('الحد الأقصى لقيمة الطلب لتطبيق الكوبون')
    )
    
    # Date Constraints
    valid_from = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ البداية'),
        help_text=_('تاريخ بداية صلاحية الكوبون')
    )
    valid_to = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ النهاية'),
        help_text=_('تاريخ انتهاء صلاحية الكوبون')
    )
    
    # Status Control
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل الكوبون نشط ومتاح للاستخدام')
    )
    
    # Targeting (Optional)
    applicable_products = models.ManyToManyField(
        'Product',
        blank=True,
        verbose_name=_('المنتجات المطبقة'),
        help_text=_('المنتجات التي يمكن تطبيق الكوبون عليها')
    )
    applicable_categories = models.ManyToManyField(
        'Category',
        blank=True,
        verbose_name=_('الفئات المطبقة'),
        help_text=_('الفئات التي يمكن تطبيق الكوبون عليها')
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
        verbose_name = _('كوبون')
        verbose_name_plural = _('كوبونات')
        indexes = [
            models.Index(fields=['code'], name='coupon_code_idx'),
            models.Index(fields=['is_active'], name='coupon_active_idx'),
            models.Index(fields=['valid_from', 'valid_to'], name='coupon_dates_idx'),
            models.Index(fields=['used_count'], name='coupon_usage_idx'),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name or 'Untitled'}"
    
    def clean(self):
        """Validate coupon data"""
        super().clean()
        
        # Validate discount value
        if self.discount_type == 'percentage' and (self.discount_value <= 0 or self.discount_value > 100):
            raise ValidationError({
                'discount_value': _('نسبة الخصم يجب أن تكون بين 0 و 100')
            })
        
        if self.discount_type == 'fixed' and self.discount_value <= 0:
            raise ValidationError({
                'discount_value': _('مبلغ الخصم يجب أن يكون أكبر من 0')
            })
        
        # Validate dates
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError({
                'valid_to': _('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
            })
        
        # Validate max discount for percentage
        if self.discount_type == 'percentage' and self.max_discount and self.max_discount <= 0:
            raise ValidationError({
                'max_discount': _('أقصى خصم يجب أن يكون أكبر من 0')
            })
    
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
        related_name='couponusage',
        verbose_name=_('الكوبون')
    )
    user = models.ForeignKey(
        'api.User',
        on_delete=models.CASCADE,
        related_name='couponusage',
        verbose_name=_('المستخدم')
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='couponusage',
        verbose_name=_('الطلب')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('مبلغ الخصم')
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الاستخدام')
    )
    
    class Meta:
        db_table = 'api_coupon_usage'
        verbose_name = _('استخدام كوبون')
        verbose_name_plural = _('استخدامات الكوبونات')
        unique_together = ['coupon', 'user', 'order']
        indexes = [
            models.Index(fields=['coupon', 'user'], name='coupon_usage_user_idx'),
            models.Index(fields=['used_at'], name='coupon_usage_date_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"


# Post-migrate signal to create default coupons
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_coupons(sender, **kwargs):
    """Create default coupons after migration"""
    if sender.name == 'api':
        from django.utils import timezone
        from datetime import timedelta
        
        if not Coupon.objects.filter(code='WELCOME10').exists():
            welcome_coupon = Coupon.objects.create(
                code='WELCOME10',
                name=_('كوبون الترحيب'),
                description=_('خصم 10% على أول طلب'),
                discount_type='percentage',
                discount_value=10,
                min_order_value=1000,
                usage_limit=100,
                usage_limit_per_user=1,
                valid_from=timezone.now(),
                valid_to=timezone.now() + timedelta(days=30),
                is_active=True
            )
            print(f"✅ Created welcome coupon: {welcome_coupon.code}")
        
        if not Coupon.objects.filter(code='SUMMER2024').exists():
            summer_coupon = Coupon.objects.create(
                code='SUMMER2024',
                name=_('كوبون الصيف'),
                description=_('خصم 500 دينار جزائري على الطلبات فوق 5000'),
                discount_type='fixed',
                discount_value=500,
                min_order_value=5000,
                usage_limit=50,
                usage_limit_per_user=1,
                valid_from=timezone.now(),
                valid_to=timezone.now() + timedelta(days=90),
                is_active=True
            )
            print(f"✅ Created summer coupon: {summer_coupon.code}")
