"""
GraphQL Schema for Organization and Social Media models
Updated to include new relational fields and platform types
"""

import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field_with_choices
from django.contrib.auth import get_user_model

from .organization import Organization, Social, PlatformType
from core.models import Shipping


User = get_user_model()


class UserObjectType(DjangoObjectType):
    """
    GraphQL type for User model
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ShippingObjectType(DjangoObjectType):
    """
    GraphQL type for Shipping model (from core app)
    """
    class Meta:
        model = Shipping
        fields = (
            'id', 'wilaya_id', 'name_ar', 'name_fr', 
            'stop_desk_price', 'home_delivery_price', 'is_active', 'regions',
            'pickup_latitude', 'pickup_longitude', 'radius_km', 'maps_url',
            'created_at', 'updated_at'
        )


class SocialObjectType(DjangoObjectType):
    """
    GraphQL type for Social Media links with new fields
    """
    platform_type_display_name = graphene.String()
    platform_display_name = graphene.String()
    fa_icon_class = graphene.String()
    
    class Meta:
        model = Social
        fields = (
            'id', 'organization', 'platform_name', 'platform_display_name',
            'platform_type', 'platform_type_display_name', 'url', 
            'icon_class', 'fa_icon_class', 'order_index', 'is_active',
            'created_at', 'updated_at'
        )
    
    def resolve_platform_type_display_name(self, info):
        """
        Resolve platform type display name
        """
        return self.get_platform_type_display_name()
    
    def resolve_platform_display_name(self, info):
        """
        Resolve platform display name
        """
        return self.get_platform_display_name()
    
    def resolve_fa_icon_class(self, info):
        """
        Resolve Font Awesome icon class
        """
        return self.get_fa_icon_class()


class OrganizationObjectType(DjangoObjectType):
    """
    GraphQL type for Organization with new relational fields
    """
    name = graphene.String()
    slogan = graphene.String()
    about = graphene.String()
    contact_info = graphene.JSONString()
    social_links = graphene.List(SocialObjectType)
    created_by_user = graphene.Field(UserObjectType)
    base_city_info = graphene.Field(ShippingObjectType)
    
    class Meta:
        model = Organization
        fields = (
            'id', 'name_ar', 'name_en', 'name', 'logo', 
            'slogan_ar', 'slogan_en', 'slogan',
            'about_ar', 'about_en', 'about',
            'contact_email', 'phone_1', 'phone_2', 'address', 
            'latitude', 'longitude', 'google_place_id', 'maps_url',
            'tax_number', 'created_by', 'created_by_user', 'base_city', 
            'base_city_info', 'contact_info', 'social_links', 'is_active',
            'created_at', 'updated_at'
        )
    
    def resolve_name(self, info):
        """
        Resolve name based on request language
        """
        language = info.context.headers.get('Accept-Language', 'ar').split(',')[0].split('-')[0]
        return self.get_name(language)
    
    def resolve_slogan(self, info):
        """
        Resolve slogan based on request language
        """
        language = info.context.headers.get('Accept-Language', 'ar').split(',')[0].split('-')[0]
        return self.get_slogan(language)
    
    def resolve_about(self, info):
        """
        Resolve about text based on request language
        """
        language = info.context.headers.get('Accept-Language', 'ar').split(',')[0].split('-')[0]
        return self.get_about(language)
    
    def resolve_contact_info(self, info):
        """
        Resolve formatted contact information
        """
        return self.get_contact_info()
    
    def resolve_social_links(self, info):
        """
        Resolve active social links ordered by index
        """
        return self.social_links.filter(is_active=True).order_by('order_index', 'platform_name')
    
    def resolve_created_by_user(self, info):
        """
        Resolve user who created the organization
        """
        return self.created_by
    
    def resolve_base_city_info(self, info):
        """
        Resolve base city information
        """
        return self.base_city


class OrganizationQuery(graphene.ObjectType):
    """
    GraphQL queries for Organization and Social Media
    """
    organization = graphene.Field(OrganizationObjectType)
    organizations = graphene.List(OrganizationObjectType)
    social_links = graphene.List(SocialObjectType, organization_id=graphene.ID())
    social_links_by_type = graphene.List(
        SocialObjectType, 
        organization_id=graphene.ID(),
        platform_type=graphene.String()
    )
    
    def resolve_organization(self, info):
        """
        Get active organization instance
        """
        try:
            return Organization.objects.get_instance()
        except Organization.DoesNotExist:
            return None
    
    def resolve_organizations(self, info):
        """
        Get all organizations (for admin purposes)
        """
        return Organization.objects.all().select_related('created_by', 'base_city').order_by('-created_at')
    
    def resolve_social_links(self, info, organization_id=None):
        """
        Get social links for specific organization
        """
        if not organization_id:
            return []
        
        try:
            org = Organization.objects.get(pk=organization_id)
            return org.social_links.filter(is_active=True).order_by('order_index')
        except Organization.DoesNotExist:
            return []
    
    def resolve_social_links_by_type(self, info, organization_id=None, platform_type=None):
        """
        Get social links filtered by platform type
        """
        if not organization_id:
            return []
        
        try:
            org = Organization.objects.get(pk=organization_id)
            queryset = org.social_links.filter(is_active=True)
            
            if platform_type:
                queryset = queryset.filter(platform_type=platform_type)
            
            return queryset.order_by('order_index')
        except Organization.DoesNotExist:
            return []


class CreateSocialLink(graphene.Mutation):
    """
    GraphQL mutation to create social media link
    """
    class Arguments:
        organization_id = graphene.ID(required=True)
        platform_name = graphene.String(required=True)
        platform_type = graphene.String(required=True)
        url = graphene.String(required=True)
        icon_class = graphene.String(required=True)
        order_index = graphene.Int(required=False, default_value=0)
    
    success = graphene.Boolean()
    message = graphene.String()
    social_link = graphene.Field(SocialObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Create new social media link
        """
        try:
            organization = Organization.objects.get_instance()
            
            # Validate platform_type
            if kwargs.get('platform_type') not in dict(PlatformType.choices).values():
                return CreateSocialLink(
                    success=False,
                    message='نوع المنصة غير صالح'
                )
            
            social_link = Social.objects.create(
                organization=organization,
                **kwargs
            )
            
            return CreateSocialLink(
                success=True,
                message='تم إضافة الرابط الاجتماعي بنجاح',
                social_link=social_link
            )
            
        except Organization.DoesNotExist:
            return CreateSocialLink(
                success=False,
                message='لا توجد مؤسسة نشطة'
            )
        except Exception as e:
            return CreateSocialLink(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class UpdateSocialLink(graphene.Mutation):
    """
    GraphQL mutation to update social media link
    """
    class Arguments:
        id = graphene.ID(required=True)
        platform_name = graphene.String(required=False)
        platform_type = graphene.String(required=False)
        url = graphene.String(required=False)
        icon_class = graphene.String(required=False)
        order_index = graphene.Int(required=False)
        is_active = graphene.Boolean(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    social_link = graphene.Field(SocialObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Update existing social media link
        """
        try:
            social_link = Social.objects.get(pk=kwargs.pop('id'))
            
            # Validate platform_type if provided
            platform_type = kwargs.get('platform_type')
            if platform_type and platform_type not in dict(PlatformType.choices).values():
                return UpdateSocialLink(
                    success=False,
                    message='نوع المنصة غير صالح'
                )
            
            for field, value in kwargs.items():
                if value is not None:
                    setattr(social_link, field, value)
            
            social_link.save()
            
            return UpdateSocialLink(
                success=True,
                message='تم تحديث الرابط الاجتماعي بنجاح',
                social_link=social_link
            )
            
        except Social.DoesNotExist:
            return UpdateSocialLink(
                success=False,
                message='الرابط غير موجود'
            )
        except Exception as e:
            return UpdateSocialLink(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class DeleteSocialLink(graphene.Mutation):
    """
    GraphQL mutation to delete social media link
    """
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        """
        Delete social media link
        """
        try:
            social_link = Social.objects.get(pk=id)
            social_link.delete()
            
            return DeleteSocialLink(
                success=True,
                message='تم حذف الرابط الاجتماعي بنجاح'
            )
            
        except Social.DoesNotExist:
            return DeleteSocialLink(
                success=False,
                message='الرابط غير موجود'
            )
        except Exception as e:
            return DeleteSocialLink(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class UpdateOrganizationMaps(graphene.Mutation):
    """
    GraphQL mutation to update organization Google Maps information
    """
    class Arguments:
        id = graphene.ID(required=True)
        latitude = graphene.Decimal(required=False)
        longitude = graphene.Decimal(required=False)
        google_place_id = graphene.String(required=False)
        maps_url = graphene.String(required=False)
        address = graphene.String(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    organization = graphene.Field(OrganizationObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Update organization Google Maps information
        """
        try:
            organization = Organization.objects.get(pk=kwargs.pop('id'))
            
            for field, value in kwargs.items():
                if value is not None:
                    setattr(organization, field, value)
            
            organization.save()
            
            return UpdateOrganizationMaps(
                success=True,
                message='تم تحديث معلومات الخريطة بنجاح',
                organization=organization
            )
            
        except Organization.DoesNotExist:
            return UpdateOrganizationMaps(
                success=False,
                message='المؤسسة غير موجودة'
            )
        except Exception as e:
            return UpdateOrganizationMaps(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class UpdateShippingMaps(graphene.Mutation):
    """
    GraphQL mutation to update shipping Google Maps information
    """
    class Arguments:
        id = graphene.ID(required=True)
        pickup_latitude = graphene.Decimal(required=False)
        pickup_longitude = graphene.Decimal(required=False)
        radius_km = graphene.Int(required=False)
        maps_url = graphene.String(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    shipping = graphene.Field(ShippingObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Update shipping Google Maps information
        """
        try:
            shipping = Shipping.objects.get(pk=kwargs.pop('id'))
            
            for field, value in kwargs.items():
                if value is not None:
                    setattr(shipping, field, value)
            
            shipping.save()
            
            return UpdateShippingMaps(
                success=True,
                message='تم تحديث معلومات خريطة الشحن بنجاح',
                shipping=shipping
            )
            
        except Shipping.DoesNotExist:
            return UpdateShippingMaps(
                success=False,
                message='منطقة الشحن غير موجودة'
            )
        except Exception as e:
            return UpdateShippingMaps(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class UpdateOrganization(graphene.Mutation):
    """
    GraphQL mutation to update organization information (superuser only)
    """
    class Arguments:
        id = graphene.ID(required=True)
        name_ar = graphene.String(required=False)
        name_en = graphene.String(required=False)
        slogan_ar = graphene.String(required=False)
        slogan_en = graphene.String(required=False)
        about_ar = graphene.String(required=False)
        about_en = graphene.String(required=False)
        contact_email = graphene.String(required=False)
        phone_1 = graphene.String(required=False)
        phone_2 = graphene.String(required=False)
        address = graphene.String(required=False)
        tax_number = graphene.String(required=False)
        latitude = graphene.Decimal(required=False)
        longitude = graphene.Decimal(required=False)
        google_place_id = graphene.String(required=False)
        maps_url = graphene.String(required=False)
        base_city_id = graphene.ID(required=False)
        is_active = graphene.Boolean(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    organization = graphene.Field(OrganizationObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Update organization information (superuser only)
        """
        # Check if user is authenticated and is superuser
        if not info.context.user.is_authenticated:
            return UpdateOrganization(
                success=False,
                message='المصادقة مطلوبة'
            )
        
        if not info.context.user.is_superuser:
            return UpdateOrganization(
                success=False,
                message='فقط المستخدم المتميز يمكنه تحديث بيانات المؤسسة'
            )
        
        try:
            organization = Organization.objects.get(pk=kwargs.pop('id'))
            
            # Handle base_city_id separately
            base_city_id = kwargs.pop('base_city_id', None)
            if base_city_id is not None:
                try:
                    from core.models import Shipping
                    base_city = Shipping.objects.get(pk=base_city_id)
                    organization.base_city = base_city
                except Shipping.DoesNotExist:
                    return UpdateOrganization(
                        success=False,
                        message='المدينة المحددة غير موجودة'
                    )
            
            # Update other fields
            for field, value in kwargs.items():
                if value is not None:
                    setattr(organization, field, value)
            
            organization.save()
            
            return UpdateOrganization(
                success=True,
                message='تم تحديث بيانات المؤسسة بنجاح',
                organization=organization
            )
            
        except Organization.DoesNotExist:
            return UpdateOrganization(
                success=False,
                message='المؤسسة غير موجودة'
            )
        except Exception as e:
            return UpdateOrganization(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class OrganizationMutation(graphene.ObjectType):
    """
    GraphQL mutations for Organization and Social Media
    """
    create_social_link = CreateSocialLink.Field()
    update_social_link = UpdateSocialLink.Field()
    delete_social_link = DeleteSocialLink.Field()
    update_organization_maps = UpdateOrganizationMaps.Field()
    update_shipping_maps = UpdateShippingMaps.Field()
    update_organization = UpdateOrganization.Field()


# Complete schema with organization queries and mutations
schema = graphene.Schema(
    query=OrganizationQuery,
    mutation=OrganizationMutation
)
