"""
Organization and Social Media Models for VinylArt
Supports company identity management with multilingual content and relational integrity
"""

from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
from django.utils.translation import gettext_lazy as _
from .shipping import Shipping


class OrganizationManager(models.Manager):
    """
    Custom manager for Organization model implementing Singleton pattern
    """
    def get_instance(self):
        """
        Get single active organization instance
        """
        instance, created = self.get_or_create(
            defaults={
                'name_ar': 'VinylArt',
                'name_en': 'VinylArt',
                'contact_email': 'info@vinylart.dz',
                'is_active': True
            }
        )
        return instance


class Organization(models.Model):
    """
    Organization Identity Model - Singleton Pattern
    Stores company information with Arabic and English support and proper relational links
    """
    
    # Basic Information (Bilingual)
    name_ar = models.CharField(
        max_length=255,
        verbose_name=_('الاسم بالعربية'),
        help_text=_('اسم المؤسسة باللغة العربية'),
        default='VinylArt'
    )
    name_en = models.CharField(
        max_length=255,
        verbose_name=_('الاسم بالإنجليزية'),
        help_text=_('اسم المؤسسة باللغة الإنجليزية'),
        default='VinylArt'
    )
    
    # Visual Identity (Bilingual)
    logo = models.ImageField(
        upload_to='org/logo/',
        max_length=255,
        verbose_name=_('الشعار'),
        help_text=_('شعار المؤسسة')
    )
    slogan_ar = models.CharField(
        max_length=500,
        verbose_name=_('الشعار بالعربية'),
        help_text=_('الشعار التسويقي بالعربية')
    )
    slogan_en = models.CharField(
        max_length=500,
        verbose_name=_('الشعار بالإنجليزية'),
        help_text=_('الشعار التسويقي بالإنجليزية')
    )
    
    # About Section (Bilingual)
    about_ar = models.TextField(
        verbose_name=_('نبذة بالعربية'),
        help_text=_('قصة المؤسسة ونبذة عنها بالعربية')
    )
    about_en = models.TextField(
        verbose_name=_('نبذة بالإنجليزية'),
        help_text=_('قصة المؤسسة ونبذة عنها بالإنجليزية')
    )
    
    # Contact Information (Proper Field Types)
    contact_email = models.EmailField(
        max_length=255,
        verbose_name=_('البريد الإلكتروني للتواصل'),
        help_text=_('البريد الرسمي للتواصل')
    )
    phone_1 = models.CharField(
        max_length=20,
        verbose_name=_('الهاتف الأول'),
        help_text=_('رقم الهاتف الرئيسي')
    )
    phone_2 = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('الهاتف الثاني'),
        help_text=_('رقم الهاتف الثانوي')
    )
    address = models.TextField(
        verbose_name=_('العنوان'),
        help_text=_('عنوان المقر الرئيسي')
    )
    
    # Google Maps Integration
    latitude = models.DecimalField(
        max_digits=22,
        decimal_places=16,
        null=True,
        blank=True,
        verbose_name=_('خط العرض'),
        help_text=_('إحداثيات خط العرض من جوجل مابس')
    )
    longitude = models.DecimalField(
        max_digits=22,
        decimal_places=16,
        null=True,
        blank=True,
        verbose_name=_('خط الطول'),
        help_text=_('إحداثيات خط الطول من جوجل مابس')
    )
    google_place_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('معرف المكان في جوجل'),
        help_text=_('معرف المكان من جوجل لضمان فتح الخريطة بدقة')
    )
    maps_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('رابط الخريطة'),
        help_text=_('رابط مباشر لخرائط جوجل')
    )
    
    # Business Information
    tax_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('الرقم الضريبي'),
        help_text=_('الرقم الجبائي (NIF/NIS)')
    )
    
    # Relational Links
    created_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('that created the record'),
        help_text=_('User who created the record'),
        related_name='created_organizations'
    )
    created_by_user = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Created by User'),
        help_text=_('User who created the record (alias for created_by)'),
        related_name='created_by_user_organizations'
    )
    base_city = models.ForeignKey(
        Shipping,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name=_('Base City'),
        help_text=_('City where the headquarters is located'),
        related_name='organizations'
    )
    
    # Status and Timestamps
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل المؤسسة نشطة حالياً')
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
    objects = OrganizationManager()
    
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ['-created_at']
        db_table = 'api_organization'
        db_tablespace = ''
        constraints = [
            models.UniqueConstraint(
                fields=['id'],
                condition=models.Q(is_active=True),
                name='singleton_active_organization'
            )
        ]
        indexes = [
            models.Index(fields=['is_active'], name='org_is_active_idx'),
            models.Index(fields=['base_city'], name='org_base_city_idx'),
            models.Index(fields=['created_by'], name='org_created_by_idx'),
        ]
    
    def __str__(self):
        return self.name_ar or self.name_en or 'VinylArt'
    
    def get_name(self, language='ar'):
        """
        Get organization name based on language
        """
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name_ar or self.name_en
    
    def get_slogan(self, language='ar'):
        """
        Get slogan based on language
        """
        if language == 'en' and self.slogan_en:
            return self.slogan_en
        return self.slogan_ar or self.slogan_en
    
    def get_about(self, language='ar'):
        """
        Get about text based on language
        """
        if language == 'en' and self.about_en:
            return self.about_en
        return self.about_ar or self.about_en
    
    def get_contact_info(self):
        """
        Get formatted contact information
        """
        return {
            'email': self.contact_email,
            'phones': [phone for phone in [self.phone_1, self.phone_2] if phone],
            'address': self.address,
            'tax_number': self.tax_number,
            'city': self.base_city.name_ar if self.base_city else None
        }
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce singleton pattern
        """
        if self.is_active:
            # Deactivate all other active organizations
            Organization.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class PlatformType(models.TextChoices):
    """
    Choices for social media platform types
    """
    PUBLIC = 'public', _('عام (للزبائن)')
    INTERNAL = 'internal', _('داخلي (للموظفين)')
    PARTNERS = 'partners', _('شركاء')


class Social(models.Model):
    """
    Social Media Links Model
    Stores organization's social media profiles with proper relational linkage and ordering
    """
    
    # Foreign Key with proper related_name
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name=_('المؤسسة'),
        related_name='social_links'
    )
    
    # Platform Information
    platform_name = models.CharField(
        max_length=50,
        verbose_name=_('اسم المنصة'),
        help_text=_('مثل: Facebook, TikTok, Instagram')
    )
    platform_type = models.CharField(
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.PUBLIC,
        verbose_name=_('نوع المنصة'),
        help_text=_('هل الرابط للزبائن أم للموظفين أم للشركاء')
    )
    url = models.URLField(
        max_length=500,
        verbose_name=_('الرابط'),
        help_text=_('رابط الحساب على المنصة')
    )
    icon_class = models.CharField(
        max_length=100,
        verbose_name=_('كود الأيقونة'),
        help_text=_('مثل: fa-brands fa-facebook, fa-brands fa-instagram')
    )
    
    # Ordering and Status
    order_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('ترتيب الظهور'),
        help_text=_('ترتيب ظهور الرابط في القائمة')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل الرابط نشط ومرئي')
    )
    
    # Timestamps and Audit
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    class Meta:
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')
        ordering = ['order_index', 'platform_name']
        db_table = 'api_social'
        db_tablespace = ''
        indexes = [
            models.Index(fields=['platform_name'], name='social_platform_name_idx'),
            models.Index(fields=['is_active'], name='social_is_active_idx'),
            models.Index(fields=['organization', 'is_active'], name='social_org_active_idx'),
            models.Index(fields=['platform_type'], name='social_platform_type_idx'),
            models.Index(fields=['order_index'], name='social_order_idx'),
        ]
        unique_together = [
            ['organization', 'platform_name']
        ]
    
    def __str__(self):
        return f"{self.organization.name_ar} - {self.platform_name}"
    
    def clean(self):
        """
        Validate URL format
        """
        if self.url:
            validator = URLValidator()
            try:
                validator(self.url)
            except ValidationError:
                raise ValidationError({'url': _('الرابط غير صحيح')})
    
    def get_platform_display_name(self):
        """
        Get user-friendly platform name
        """
        platform_names = {
            'facebook': 'فيسبوك',
            'twitter': 'تويتر',
            'instagram': 'إنستغرام',
            'linkedin': 'لينكدإن',
            'youtube': 'يوتيوب',
            'tiktok': 'تيك توك',
            'whatsapp': 'واتساب',
            'telegram': 'تيليجرام',
            'snapchat': 'سناب شات',
            'pinterest': 'بينترست',
        }
        return platform_names.get(self.platform_name.lower(), self.platform_name)
    
    def get_platform_type_display_name(self):
        """
        Get user-friendly platform type name
        """
        return dict(PlatformType.choices).get(self.platform_type, self.platform_type)
    
    def get_fa_icon_class(self):
        """
        Get Font Awesome icon class with fallback
        """
        if self.icon_class:
            return self.icon_class
        
        # Default icons for common platforms
        default_icons = {
            'facebook': 'fa-brands fa-facebook',
            'twitter': 'fa-brands fa-twitter',
            'instagram': 'fa-brands fa-instagram',
            'linkedin': 'fa-brands fa-linkedin',
            'youtube': 'fa-brands fa-youtube',
            'tiktok': 'fa-brands fa-tiktok',
            'whatsapp': 'fa-brands fa-whatsapp',
            'telegram': 'fa-brands fa-telegram',
            'snapchat': 'fa-brands fa-snapchat',
            'pinterest': 'fa-brands fa-pinterest',
        }
        return default_icons.get(self.platform_name.lower(), 'fa-solid fa-link')


# Signal handlers for automatic organization creation and singleton enforcement
from django.db.models.signals import post_migrate, pre_save
from django.dispatch import receiver
from django.db import transaction


@receiver(pre_save, sender=Organization)
def enforce_organization_singleton(sender, instance, **kwargs):
    """
    Prevent creation of multiple active organizations
    """
    if instance.is_active:
        with transaction.atomic():
            Organization.objects.filter(is_active=True).exclude(pk=instance.pk).update(is_active=False)


# @receiver(post_migrate)
# def create_default_organization(sender, **kwargs):
#     """
#     Create default organization instance after migration
#     """
#     if sender.name == 'api':
#         Organization.objects.get_instance()
