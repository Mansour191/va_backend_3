"""
Admin configuration for Organization and Social Media models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..models.organization import Organization, Social


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Organization model
    Implements singleton pattern - only one active organization allowed
    """
    
    list_display = [
        'name_ar', 'name_en', 'contact_email', 'phone_1', 'is_active', 'updated_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_ar', 'name_en', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': (
                'name_ar', 'name_en', 'logo', 'is_active'
            ),
            'classes': ('wide',),
        }),
        ('الشعار والنبذة', {
            'fields': (
                'slogan_ar', 'slogan_en', 'about_ar', 'about_en'
            ),
            'classes': ('wide',),
        }),
        ('معلومات التواصل', {
            'fields': (
                'contact_email', 'phone_1', 'phone_2', 'address', 'tax_number'
            ),
            'classes': ('wide',),
        }),
        ('معلومات النظام', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',),
        }),
    )
    
    # def has_add_permission(self, request):
    #     """
    #     Only allow adding if no active organization exists
    #     """
    #     return not Organization.objects.filter(is_active=True).exists()
    
    def has_add_permission(self, request):
        """
        Temporarily disabled - always allow adding
        """
        return True
    
    def get_queryset(self, request):
        """
        Show only the most recent organization in list view
        """
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')
    
    def response_add(self, request, obj, post_url_continue=None):
        """
        Deactivate other organizations when new one is created
        """
        Organization.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """
        Handle organization changes
        """
        if obj.is_active:
            Organization.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        return super().response_change(request, obj)
    
    def logo_preview(self, obj):
        """
        Show logo preview in admin list
        """
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.logo.url
            )
        return mark_safe('<span style="color: #999;">لا يوجد شعار</span>')
    logo_preview.short_description = _('معاينة الشعار')
    logo_preview.allow_tags = True
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make created_at and updated_at readonly
        """
        readonly = list(self.readonly_fields)
        if obj:  # editing existing object
            readonly.extend(['created_at'])
        return readonly


class SocialInline(admin.TabularInline):
    """
    Inline admin for Social Media links
    """
    model = Social
    extra = 3
    min_num = 0
    fields = (
        'platform_name', 'url', 'icon_class', 'order_index', 'is_active'
    )
    ordering = ('order_index', 'platform_name')
    
    def get_queryset(self, request):
        """
        Only show social links for active organization
        """
        qs = super().get_queryset(request)
        try:
            org = Organization.objects.get_instance()
            return qs.filter(organization=org)
        except:
            return qs.none()


@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    """
    Admin configuration for Social Media model
    """
    
    list_display = [
        'platform_name', 'organization', 'url_preview', 'order_index', 'is_active', 'updated_at'
    ]
    list_filter = ['platform_name', 'is_active', 'organization']
    search_fields = ['platform_name', 'url', 'organization__name_ar', 'organization__name_en']
    list_editable = ['order_index', 'is_active']
    ordering = ['order_index', 'platform_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': (
                'organization', 'platform_name', 'url', 'icon_class'
            ),
            'classes': ('wide',),
        }),
        ('العرض والتحكم', {
            'fields': (
                'order_index', 'is_active'
            ),
            'classes': ('wide',),
        }),
        ('معلومات النظام', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',),
        }),
    )
    
    def url_preview(self, obj):
        """
        Show URL preview with link
        """
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
                obj.url,
                obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
            )
        return '-'
    url_preview.short_description = _('رابط')
    url_preview.allow_tags = True
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Customize form based on user permissions
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text for platform names
        if 'platform_name' in form.base_fields:
            form.base_fields['platform_name'].help_text = _(
                'أسماء المنصات الشائعة: Facebook, Twitter, Instagram, LinkedIn, YouTube, TikTok, WhatsApp, Telegram, Snapchat, Pinterest'
            )
        
        # Add help text for icon classes
        if 'icon_class' in form.base_fields:
            form.base_fields['icon_class'].help_text = _(
                'أمثلة: fa-brands fa-facebook, fa-brands fa-instagram, fa-solid fa-link'
            )
        
        return form
    
    def get_queryset(self, request):
        """
        Filter based on user permissions
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers can only see social links of active organization
            try:
                org = Organization.objects.get_instance()
                qs = qs.filter(organization=org)
            except:
                qs = qs.none()
        return qs.select_related('organization')


# Customize admin site header and title
admin.site.site_header = mark_safe('VinylArt <span style="font-size: 14px; color: #666;">إدارة المحتوى</span>')
admin.site.site_title = _('VinylArt Administration')
admin.site.index_title = _('مرحباً بك في لوحة تحكم VinylArt')
