"""
Payment Method Models for VinylArt
Supports configurable payment methods with multilingual instructions and account details
"""

from django.db import models
from django.utils import timezone
import json
from django.utils.translation import gettext_lazy as _


class PaymentMethodManager(models.Manager):
    """
    Custom manager for PaymentMethod model
    """
    def get_active_methods(self):
        """
        Get only active payment methods for customers
        """
        return self.filter(is_active=True).order_by('order_index', 'name_ar')
    
    def get_all_methods(self):
        """
        Get all payment methods for admin
        """
        return self.all().order_by('order_index', 'name_ar')


class PaymentMethod(models.Model):
    """
    Payment Method Model - System Configurable Payment Options
    Stores payment methods that can be enabled/disabled by administrators
    """
    
    # Basic Information (Bilingual)
    name_ar = models.CharField(
        max_length=100,
        verbose_name=_('الاسم بالعربية'),
        help_text=_('اسم طريقة الدفع بالعربية')
    )
    name_en = models.CharField(
        max_length=100,
        verbose_name=_('الاسم بالإنجليزية'),
        help_text=_('اسم طريقة الدفع بالإنجليزية')
    )
    
    # Payment Type and Gateway
    payment_type = models.CharField(
        max_length=20,
        choices=[
            ('cash', _('الدفع عند الاستلام')),
            ('bank_transfer', _('تحويل بنكي')),
            ('wallet', _('محفظة إلكترونية')),
            ('card', _('بطاقة بنكية')),
            ('other', _('أخرى'))
        ],
        default='cash',
        verbose_name=_('نوع الدفع'),
        help_text=_('نوع طريقة الدفع')
    )
    
    gateway_provider = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('مزود البوابة'),
        help_text=_('مزود بوابة الدفع (مثل: CIB, BaridiMob)')
    )
    
    # Account Information (Sensitive Data)
    account_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('اسم الحساب'),
        help_text=_('اسم صاحب الحساب أو المستفيد')
    )
    account_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('رقم الحساب/الحساب البريدي الجاري'),
        help_text=_('رقم الحساب البنكي أو الحساب البريدي الجاري (CCP)')
    )
    iban = models.CharField(
        max_length=34,
        blank=True,
        null=True,
        verbose_name=_('IBAN'),
        help_text=_('رقم الحساب البنكي الدولي (IBAN)'),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$',
                message=_('IBAN غير صالح')
            )
        ]
    )
    
    # Instructions (Bilingual)
    instructions_ar = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('التعليمات بالعربية'),
        help_text=_('تعليمات الدفع للزبائن بالعربية')
    )
    instructions_en = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('التعليمات بالإنجليزية'),
        help_text=_('تعليمات الدفع للزبائن بالإنجليزية')
    )
    
    # Visual Elements
    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('الأيقونة'),
        help_text=_('كود أيقونة Font Awesome (مثل: fas fa-university)')
    )
    logo = models.ImageField(
        upload_to='payment_methods/logos/',
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('الشعار'),
        help_text=_('شعار البنك أو خدمة الدفع')
    )
    
    # Display and Control
    order_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('ترتيب الظهور'),
        help_text=_('ترتيب ظهور طريقة الدفع في القائمة')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل طريقة الدفع نشطة ومتاحة للزبائن')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('افتراضي'),
        help_text=_('طريقة الدفع الافتراضية (واحدة فقط)')
    )
    
    # Additional Configuration
    max_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('الحد الأقصى للمبلغ'),
        help_text=_('الحد الأقصى للمبلغ المسموح بهذه الطريقة')
    )
    fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('نسبة الرسوم'),
        help_text=_('نسبة الرسوم المضافة للمبلغ (%)')
    )
    fee_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('رسوم ثابتة'),
        help_text=_('رسوم ثابتة مضافة للمبلغ')
    )
    
    # Audit Fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('أنشئ بواسطة'),
        help_text=_('المستخدم الذي أنشأ طريقة الدفع'),
        related_name='created_payment_methods'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    # Custom Manager
    objects = PaymentMethodManager()
    
    class Meta:
        verbose_name = _('طريقة دفع')
        verbose_name_plural = _('طرق الدفع')
        ordering = ['order_index', 'name_ar']
        db_table = 'api_payment_method'
        db_tablespace = ''
        indexes = [
            models.Index(fields=['is_active'], name='payment_method_is_active_idx'),
            models.Index(fields=['payment_type'], name='payment_method_type_idx'),
            models.Index(fields=['order_index'], name='payment_method_order_idx'),
            models.Index(fields=['is_default'], name='payment_method_default_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['is_default'],
                condition=models.Q(is_default=True),
                name='single_default_payment_method'
            )
        ]
    
    def __str__(self):
        return self.get_name()
    
    def get_name(self, language='ar'):
        """
        Get payment method name based on language
        """
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name_ar or self.name_en
    
    def get_instructions(self, language='ar'):
        """
        Get payment instructions based on language
        """
        if language == 'en' and self.instructions_en:
            return self.instructions_en
        return self.instructions_ar or self.instructions_en
    
    def get_display_icon(self):
        """
        Get Font Awesome icon class with fallback
        """
        if self.icon:
            return self.icon
        
        # Default icons for payment types
        default_icons = {
            'cash': 'fas fa-hand-holding-usd',
            'bank_transfer': 'fas fa-university',
            'wallet': 'fas fa-wallet',
            'card': 'fas fa-credit-card',
            'other': 'fas fa-money-bill'
        }
        return default_icons.get(self.payment_type, 'fas fa-money-bill')
    
    def calculate_fees(self, amount):
        """
        Calculate total fees for a given amount
        """
        percentage_fee = (amount * self.fee_percentage) / 100
        total_fee = percentage_fee + self.fee_fixed
        
        return {
            'percentage_fee': percentage_fee,
            'fixed_fee': self.fee_fixed,
            'total_fee': total_fee,
            'total_with_fees': amount + total_fee
        }
    
    def is_available_for_amount(self, amount):
        """
        Check if payment method is available for given amount
        """
        if not self.is_active:
            return False
        
        if self.max_amount and amount > self.max_amount:
            return False
        
        return True
    
    def get_safe_account_number(self):
        """
        Return masked account number for display
        """
        if not self.account_number:
            return ''
        
        # Show only last 4 digits for bank accounts
        if len(self.account_number) > 4:
            return '*' * (len(self.account_number) - 4) + self.account_number[-4:]
        
        return self.account_number
    
    def clean(self):
        """
        Validate model data
        """
        super().clean()
        
        # Ensure only one default payment method
        if self.is_default:
            existing_default = PaymentMethod.objects.filter(
                is_default=True
            ).exclude(pk=self.pk).exists()
            
            if existing_default:
                raise ValidationError({
                    'is_default': _('يمكن تحديد طريقة دفع واحدة فقط كافتراضية')
                })
        
        # Validate IBAN format if provided
        if self.iban:
            try:
                # Remove spaces and convert to uppercase
                iban = self.iban.replace(' ', '').upper()
                if not iban.startswith('DZ'):
                    raise ValidationError({
                        'iban': _('IBAN يجب أن يبدأ بـ DZ للجزائر')
                    })
            except Exception:
                pass  # Let the validator handle the format
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce single default
        """
        if self.is_default:
            # Set all other methods to non-default
            PaymentMethod.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


# Signal handlers for automatic setup
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_payment_methods(sender, **kwargs):
    """
    Create default payment methods after migration
    """
    if sender.name == 'api':
        from .payment_method import PaymentMethod
        
        default_methods = [
            {
                'name_ar': 'الدفع عند الاستلام',
                'name_en': 'Cash on Delivery',
                'payment_type': 'cash',
                'icon': 'fas fa-hand-holding-usd',
                'instructions_ar': 'يمكنك الدفع نقداً عند استلام المنتجات من الساعي.',
                'instructions_en': 'You can pay cash when the courier delivers your products.',
                'order_index': 1,
                'is_active': True,
                'is_default': True
            },
            {
                'name_ar': 'تحويل بنكي - CCP',
                'name_en': 'Bank Transfer - CCP',
                'payment_type': 'bank_transfer',
                'icon': 'fas fa-university',
                'instructions_ar': 'قم بتحويل المبلغ إلى الحساب البريدي الجاري (CCP) المحدد. يرجى إرسال إيصال التحويل عبر الواتساب.',
                'instructions_en': 'Transfer the amount to the specified CCP account. Please send the transfer receipt via WhatsApp.',
                'order_index': 2,
                'is_active': True,
                'is_default': False
            },
            {
                'name_ar': 'BaridiMob',
                'name_en': 'BaridiMob',
                'payment_type': 'wallet',
                'gateway_provider': 'BaridiMob',
                'icon': 'fas fa-mobile-alt',
                'instructions_ar': 'افتح تطبيق BaridiMob وقم بتحويل المبلغ إلى الرقم المحدد.',
                'instructions_en': 'Open the BaridiMob app and transfer the amount to the specified number.',
                'order_index': 3,
                'is_active': True,
                'is_default': False
            }
        ]
        
        for method_data in default_methods:
            PaymentMethod.objects.get_or_create(
                name_ar=method_data['name_ar'],
                defaults=method_data
            )
