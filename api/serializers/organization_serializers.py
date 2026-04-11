"""
Serializers for Organization and Social Media models
Updated to include new relational fields and platform types
"""

from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from api.models.organization import Organization, Social, PlatformType


User = get_user_model()


class SocialSerializer(serializers.ModelSerializer):
    """
    Serializer for Social Media links with new fields
    """
    
    platform_display_name = serializers.SerializerMethodField()
    platform_type_display_name = serializers.SerializerMethodField()
    fa_icon_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Social
        fields = [
            'id', 'platform_name', 'platform_display_name', 
            'platform_type', 'platform_type_display_name', 'url', 
            'icon_class', 'fa_icon_class', 'order_index', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_platform_display_name(self, obj):
        """
        Get user-friendly platform name in Arabic
        """
        return obj.get_platform_display_name()
    
    def get_platform_type_display_name(self, obj):
        """
        Get user-friendly platform type name
        """
        return obj.get_platform_type_display_name()
    
    def get_fa_icon_class(self, obj):
        """
        Get Font Awesome icon class with fallback
        """
        return obj.get_fa_icon_class()
    
    def validate_url(self, value):
        """
        Validate URL format
        """
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(_('الرابط يجب أن يبدأ بـ http:// أو https://'))
        return value
    
    def validate_platform_type(self, value):
        """
        Validate platform type choice
        """
        if value not in dict(PlatformType.choices).values():
            raise serializers.ValidationError(_('نوع المنصة غير صالح'))
        return value


class PlatformTypeSerializer(serializers.ModelSerializer):
    """Platform type configuration serializer"""
    class Meta:
        model = PlatformType
        fields = [
            'id', 'name', 'platform_type', 'icon', 'color',
            'base_url', 'url_template', 'is_active',
            'validation_regex', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model with new relational fields
    """
    
    social_links = SocialSerializer(many=True, read_only=True, source='social_links')
    contact_info = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    slogan = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()
    base_city_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name_ar', 'name_en', 'name', 'logo', 'logo_url',
            'slogan_ar', 'slogan_en', 'slogan', 
            'about_ar', 'about_en', 'about',
            'contact_email', 'phone_1', 'phone_2', 'address', 'tax_number',
            'created_by', 'created_by_user', 'base_city', 'base_city_info',
            'contact_info', 'social_links', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_logo_url(self, obj):
        """
        Get full logo URL
        """
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
    
    def get_name(self, obj):
        """
        Get name based on language preference
        """
        request = self.context.get('request')
        if request:
            language = getattr(request, 'LANGUAGE_CODE', 'ar')
            return obj.get_name(language)
        return obj.get_name()
    
    def get_slogan(self, obj):
        """
        Get slogan based on language preference
        """
        request = self.context.get('request')
        if request:
            language = getattr(request, 'LANGUAGE_CODE', 'ar')
            return obj.get_slogan(language)
        return obj.get_slogan()
    
    def get_about(self, obj):
        """
        Get about text based on language preference
        """
        request = self.context.get('request')
        if request:
            language = getattr(request, 'LANGUAGE_CODE', 'ar')
            return obj.get_about(language)
        return obj.get_about()
    
    def get_contact_info(self, obj):
        """
        Get formatted contact information
        """
        return obj.get_contact_info()
    
    def get_created_by_user(self, obj):
        """
        Get user who created the organization
        """
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'username': obj.created_by.username,
                'first_name': obj.created_by.first_name,
                'last_name': obj.created_by.last_name,
                'email': obj.created_by.email
            }
        return None
    
    def get_base_city_info(self, obj):
        """
        Get base city information
        """
        if obj.base_city:
            return {
                'id': obj.base_city.id,
                'name_ar': obj.base_city.name_ar,
                'name_en': obj.base_city.name_en,
                'wilaya': {
                    'id': obj.base_city.wilaya.id,
                    'name_ar': obj.base_city.wilaya.name_ar,
                    'name_en': obj.base_city.wilaya.name_en,
                    'code': obj.base_city.wilaya.code
                } if obj.base_city.wilaya else None
            }
        return None
    
    def validate_logo(self, value):
        """
        Validate logo file
        """
        if isinstance(value, InMemoryUploadedFile):
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(_('حجم الملف يجب ألا يتجاوز 5 ميجابايت'))
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    _('نوع الملف غير مدعوم. الأنواع المسموحة: JPEG, PNG, GIF, WebP')
                )
        return value
    
    def validate_contact_email(self, value):
        """
        Validate contact email format
        """
        if not value:
            raise serializers.ValidationError(_('البريد الإلكتروني مطلوب'))
        return value
    
    def validate_phone_1(self, value):
        """
        Validate primary phone number
        """
        if not value:
            raise serializers.ValidationError(_('رقم الهاتف الرئيسي مطلوب'))
        return value


class OrganizationDetailSerializer(OrganizationSerializer):
    """
    Detailed serializer for Organization with full social links and nested data
    """
    
    social_links = SocialSerializer(many=True, read_only=True, source='social_links')
    active_social_links = serializers.SerializerMethodField()
    public_social_links = serializers.SerializerMethodField()
    internal_social_links = serializers.SerializerMethodField()
    
    class Meta(OrganizationSerializer.Meta):
        fields = OrganizationSerializer.Meta.fields + [
            'active_social_links', 'public_social_links', 'internal_social_links'
        ]
    
    def get_active_social_links(self, obj):
        """
        Get only active social links ordered by index
        """
        active_links = obj.social_links.filter(is_active=True).order_by('order_index')
        return SocialSerializer(active_links, many=True, context=self.context).data
    
    def get_public_social_links(self, obj):
        """
        Get only public social links for customers
        """
        public_links = obj.social_links.filter(
            is_active=True, 
            platform_type=PlatformType.PUBLIC
        ).order_by('order_index')
        return SocialSerializer(public_links, many=True, context=self.context).data
    
    def get_internal_social_links(self, obj):
        """
        Get only internal social links for employees
        """
        internal_links = obj.social_links.filter(
            is_active=True, 
            platform_type=PlatformType.INTERNAL
        ).order_by('order_index')
        return SocialSerializer(internal_links, many=True, context=self.context).data


class SocialCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new social media links
    """
    
    class Meta:
        model = Social
        fields = [
            'platform_name', 'platform_type', 'url', 'icon_class', 'order_index', 'is_active'
        ]
    
    def validate_platform_type(self, value):
        """
        Validate platform type choice
        """
        if value not in dict(PlatformType.choices).values():
            raise serializers.ValidationError(_('نوع المنصة غير صالح'))
        return value
    
    def create(self, validated_data):
        """
        Create social link for active organization
        """
        try:
            organization = Organization.objects.get_instance()
            validated_data['organization'] = organization
            return super().create(validated_data)
        except Organization.DoesNotExist:
            raise serializers.ValidationError(_('لا توجد مؤسسة نشطة حالياً'))


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating organization information
    """
    
    class Meta:
        model = Organization
        fields = [
            'name_ar', 'name_en', 'logo', 'slogan_ar', 'slogan_en',
            'about_ar', 'about_en', 'contact_email', 'phone_1', 'phone_2',
            'address', 'tax_number', 'base_city', 'is_active'
        ]
    
    def update(self, instance, validated_data):
        """
        Update organization with singleton validation
        """
        if validated_data.get('is_active', instance.is_active):
            # Deactivate all other organizations if this one is being activated
            Organization.objects.filter(is_active=True).exclude(pk=instance.pk).update(is_active=False)
        
        return super().update(instance, validated_data)


# Response serializers for API endpoints
class OrganizationResponseSerializer(serializers.Serializer):
    """
    Standard response format for organization API
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = OrganizationDetailSerializer(required=False)
    errors = serializers.DictField(required=False)


class SocialResponseSerializer(serializers.Serializer):
    """
    Standard response format for social media API
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = SocialSerializer(required=False)
    errors = serializers.DictField(required=False)


class SocialListResponseSerializer(serializers.Serializer):
    """
    Response serializer for social links list
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = SocialSerializer(many=True, required=False)
    count = serializers.IntegerField(required=False)
    platform_type = serializers.CharField(required=False)


class OrganizationBulkActionSerializer(serializers.Serializer):
    """Organization bulk action serializer"""
    action = serializers.ChoiceField(
        choices=['activate', 'deactivate', 'verify', 'unverify'],
        required=True
    )
    organization_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    
    def validate_organization_ids(self, value):
        """Validate organization IDs exist"""
        if not Organization.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("One or more organizations not found")
        return value
    
    def save(self):
        """Execute bulk action"""
        action = self.validated_data['action']
        organization_ids = self.validated_data['organization_ids']
        organizations = Organization.objects.filter(id__in=organization_ids)
        
        if action == 'activate':
            organizations.update(is_active=True)
            message = f'{organizations.count()} organizations activated'
        
        elif action == 'deactivate':
            organizations.update(is_active=False)
            message = f'{organizations.count()} organizations deactivated'
        
        elif action == 'verify':
            organizations.update(is_verified=True)
            message = f'{organizations.count()} organizations verified'
        
        elif action == 'unverify':
            organizations.update(is_verified=False)
            message = f'{organizations.count()} organizations unverified'
        
        return {
            'status': 'success',
            'message': message,
            'affected_count': organizations.count()
        }


class SocialBulkActionSerializer(serializers.Serializer):
    """Social media bulk action serializer"""
    action = serializers.ChoiceField(
        choices=['activate', 'deactivate', 'delete'],
        required=True
    )
    social_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    
    def validate_social_ids(self, value):
        """Validate social IDs exist"""
        if not Social.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("One or more social platforms not found")
        return value
    
    def save(self):
        """Execute bulk action"""
        action = self.validated_data['action']
        social_ids = self.validated_data['social_ids']
        social_platforms = Social.objects.filter(id__in=social_ids)
        
        if action == 'activate':
            social_platforms.update(is_active=True)
            message = f'{social_platforms.count()} social platforms activated'
        
        elif action == 'deactivate':
            social_platforms.update(is_active=False)
            message = f'{social_platforms.count()} social platforms deactivated'
        
        elif action == 'delete':
            social_platforms.delete()
            message = f'{social_platforms.count()} social platforms deleted'
        
        return {
            'status': 'success',
            'message': message,
            'affected_count': social_platforms.count()
        }
