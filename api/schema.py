"""
API GraphQL Schema for VynilArt
This module provides GraphQL types and resolvers for all API models
"""
import graphene
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from .models import (
    User, UserProfile, Category, Material, Product, ProductImage, 
    ProductVariant, ProductMaterial, Shipping, Order, OrderItem, 
    OrderTimeline, Payment, Coupon, CartItem, PromotionCoupon, 
    CouponUsage, CouponCampaign, Wishlist, WishlistSettings, 
    Alert, AlertRule, SmartAlert, Review, ReviewReport, DesignCategory, 
    Design, Notification, ErpNextSyncLog, BehaviorTracking, 
    Forecast, CustomerSegment, CustomerSegmentUsers, PricingEngine, 
    BlogCategory, BlogPost, ConversationHistory, DashboardSettings,
    Organization, Social, PlatformType
)
from .schema.cart_schema import CartQuery, CartMutation, CartItemType
from .schema.wishlist_schema import WishlistQuery, WishlistMutation, WishlistType, WishlistSettingsType
from .schema.review_schema import ReviewQuery, ReviewMutation, ReviewType, ReviewReportType
from .schema.design_schema import DesignQuery, DesignMutation, DesignType, DesignCategoryType
from .schema.notification_schema import NotificationQuery, NotificationMutation, NotificationType, AlertType
from .schema.smart_alert_schema import SmartAlertQuery, SmartAlertMutation, SmartAlertType

User = get_user_model()


# Base Mixins
class IsAuthenticatedMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()


class IsStaffMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return queryset
        return queryset.none()


# ProductVariant Type
class ProductVariantType(DjangoObjectType):
    """
    GraphQL type for ProductVariant model
    """
    class Meta:
        model = ProductVariant
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'product': ['exact'],
            'sku': ['exact', 'icontains'],
            'price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'stock': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'is_active': ['exact'],
        }
    
    def resolve_attributes(self, info):
        """
        Resolve attributes JSON field
        """
        if self.attributes:
            return self.attributes
        return {}


# Product Type with variants
class ProductType(DjangoObjectType):
    """
    GraphQL type for Product model
    """
    variants = List(ProductVariantType)
    materials = List(MaterialType)
    current_price = Float()
    stock_status = String()
    is_available = Boolean()
    
    class Meta:
        model = Product
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact', 'icontains'],
            'category': ['exact'],
            'base_price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'is_active': ['exact'],
            'is_featured': ['exact'],
            'is_new': ['exact'],
            'on_sale': ['exact'],
        }
    
    def resolve_variants(self, info):
        """
        Resolve product variants
        """
        return self.variants.all()
    
    def resolve_materials(self, info):
        """
        Resolve product materials
        """
        return self.materials.all()
    
    def resolve_current_price(self, info):
        """
        Calculate current price with discount
        """
        if self.on_sale and self.discount_percent > 0:
            return float(self.base_price * (1 - self.discount_percent / 100))
        return float(self.base_price)
    
    def resolve_stock_status(self, info):
        """
        Determine stock status
        """
        if self.stock == 0:
            return 'out_of_stock'
        elif self.stock <= 10:  # Assuming reorder level is 10
            return 'low_stock'
        else:
            return 'in_stock'
    
    def resolve_is_available(self, info):
        """
        Check if product is available
        """
        return self.is_active and self.stock > 0


# Category Type
class CategoryType(DjangoObjectType):
    """
    GraphQL type for Category model
    """
    children = List('CategoryType')
    
    class Meta:
        model = Category
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact', 'icontains'],
            'parent': ['exact'],
            'is_active': ['exact'],
        }
    
    def resolve_children(self, info):
        """
        Resolve child categories
        """
        return self.children.all()


# Material Type
class MaterialType(DjangoObjectType):
    """
    GraphQL type for Material model
    """
    class Meta:
        model = Material
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_premium': ['exact'],
        }


# Shipping Type
class ShippingType(DjangoObjectType):
    """
    GraphQL type for Shipping model
    """
    regions = JSONString()
    
    class Meta:
        model = Shipping
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'wilaya_id': ['exact', 'icontains'],
            'name_ar': ['exact', 'icontains'],
            'name_fr': ['exact', 'icontains'],
            'is_active': ['exact'],
        }
    
    def resolve_regions(self, info):
        """
        Resolve regions JSON field
        """
        if self.regions:
            return self.regions
        return []


# ShippingMethod Type
class ShippingMethodType(DjangoObjectType):
    """
    GraphQL type for ShippingMethod model
    """
    delivery_days = JSONString()
    coverage_wilayas = JSONString()
    max_dimensions = JSONString()
    
    class Meta:
        model = ShippingMethod
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'provider': ['exact'],
            'service_type': ['exact'],
            'is_active': ['exact'],
        }
    
    def resolve_delivery_days(self, info):
        """
        Resolve delivery_days JSON field
        """
        if self.delivery_days:
            return self.delivery_days
        return []
    
    def resolve_coverage_wilayas(self, info):
        """
        Resolve coverage_wilayas JSON field
        """
        if self.coverage_wilayas:
            return self.coverage_wilayas
        return []
    
    def resolve_max_dimensions(self, info):
        """
        Resolve max_dimensions JSON field
        """
        if self.max_dimensions:
            return self.max_dimensions
        return {}


# ShippingPrice Type
class ShippingPriceType(DjangoObjectType):
    """
    GraphQL type for ShippingPrice model
    """
    class Meta:
        model = ShippingPrice
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'wilaya': ['exact'],
            'shipping_method': ['exact'],
            'is_active': ['exact'],
        }


# ProductImage Type
class ProductImageType(DjangoObjectType):
    """
    GraphQL type for ProductImage model
    """
    class Meta:
        model = ProductImage
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'product': ['exact'],
            'is_active': ['exact'],
        }


# User Type
class UserType(DjangoObjectType):
    """
    GraphQL type for User model
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'is_staff', 'date_joined']
        interfaces = (relay.Node,)


# UserProfile Type
class UserProfileType(DjangoObjectType):
    """
    GraphQL type for UserProfile model
    """
    user = Field(UserType)
    preferences = JSONString()
    settings = JSONString()
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        interfaces = (relay.Node,)


# Organization Type
class OrganizationType(DjangoObjectType):
    """
    GraphQL type for Organization model
    """
    logo_url = String()
    name = String()
    slogan = String()
    about = String()
    contact_info = JSONString()
    social_links = List('SocialType')
    public_social_links = List('SocialType')
    
    class Meta:
        model = Organization
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
        }
    
    def resolve_logo_url(self, info):
        """
        Resolve full logo URL
        """
        if self.logo:
            request = info.context
            if request:
                return request.build_absolute_uri(self.logo.url)
            return self.logo.url
        return None
    
    def resolve_name(self, info):
        """
        Resolve name based on language preference
        """
        request = info.context
        if request and hasattr(request, 'LANGUAGE_CODE'):
            language = getattr(request, 'LANGUAGE_CODE', 'ar')
            return self.get_name(language)
        return self.get_name()
    
    def resolve_slogan(self, info):
        """
        Resolve slogan based on language preference
        """
        request = info.context
        if request and hasattr(request, 'LANGUAGE_CODE'):
            language = getattr(request, 'LANGUAGE_CODE', 'ar')
            return self.get_slogan(language)
        return self.get_slogan()
    
    def resolve_about(self, info):
        """
        Resolve about text based on language preference
        """
        request = info.context
        if request and hasattr(request, 'LANGUAGE_CODE'):
            language = getattr(request, 'LANGUAGE_CODE', 'ar')
            return self.get_about(language)
        return self.get_about()
    
    def resolve_contact_info(self, info):
        """
        Resolve formatted contact information
        """
        return self.get_contact_info()
    
    def resolve_social_links(self, info):
        """
        Resolve all social links
        """
        return self.social_links.all()
    
    def resolve_public_social_links(self, info):
        """
        Resolve only public social links
        """
        return self.social_links.filter(
            is_active=True, 
            platform_type=PlatformType.PUBLIC
        ).order_by('order_index')


# DesignCategory Type
class DesignCategoryType(DjangoObjectType):
    """
    GraphQL type for DesignCategory model
    """
    name = String()
    
    class Meta:
        model = DesignCategory
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact', 'icontains'],
            'is_active': ['exact'],
            'design_count': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_name(self, info):
        """
        Resolve name based on current language (fallback to Arabic if English not available)
        """
        # Get language from context or default to Arabic
        language = getattr(info.context, 'LANGUAGE_CODE', 'ar')
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name_ar


# Design Type
class DesignType(DjangoObjectType):
    """
    GraphQL type for Design model
    """
    class Meta:
        model = Design
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'category': ['exact'],
            'user': ['exact'],
            'is_featured': ['exact'],
            'is_active': ['exact'],
            'status': ['exact'],
        }


# Social Type
class SocialType(DjangoObjectType):
    """
    GraphQL type for Social model
    """
    platform_display_name = String()
    platform_type_display_name = String()
    fa_icon_class = String()
    
    class Meta:
        model = Social
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'organization': ['exact'],
            'platform_name': ['exact', 'icontains'],
            'platform_type': ['exact'],
            'is_active': ['exact'],
        }
    
    def resolve_platform_display_name(self, info):
        """
        Resolve user-friendly platform name
        """
        return self.get_platform_display_name()
    
    def resolve_platform_type_display_name(self, info):
        """
        Resolve user-friendly platform type name
        """
        return self.get_platform_type_display_name()
    
    def resolve_fa_icon_class(self, info):
        """
        Resolve Font Awesome icon class with fallback
        """
        return self.get_fa_icon_class()


# ProductVariant Mutations
class CreateProductVariant(Mutation):
    """
    Mutation to create a new ProductVariant
    """
    class Arguments:
        product_id = ID(required=True)
        name = String(required=True)
        sku = String(required=True)
        price = Float(required=True)
        stock = Int(default_value=0)
        attributes = JSONString()
        is_active = Boolean(default_value=True)
    
    product_variant = Field(ProductVariantType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, product_id, name, sku, price, stock=0, attributes=None, is_active=True):
        if not info.context.user.is_authenticated:
            return CreateProductVariant(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return CreateProductVariant(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return CreateProductVariant(
                success=False,
                message="Product not found"
            )
        
        # Check if SKU already exists
        if ProductVariant.objects.filter(sku=sku).exists():
            return CreateProductVariant(
                success=False,
                message="SKU already exists"
            )
        
        # Create variant
        variant = ProductVariant.objects.create(
            product=product,
            name=name,
            sku=sku,
            price=price,
            stock=stock,
            attributes=attributes or {},
            is_active=is_active
        )
        
        return CreateProductVariant(
            product_variant=variant,
            success=True,
            message="Product variant created successfully"
        )


class UpdateProductVariant(Mutation):
    """
    Mutation to update an existing ProductVariant
    """
    class Arguments:
        id = ID(required=True)
        name = String()
        sku = String()
        price = Float()
        stock = Int()
        attributes = JSONString()
        is_active = Boolean()
    
    product_variant = Field(ProductVariantType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, id, **kwargs):
        if not info.context.user.is_authenticated:
            return UpdateProductVariant(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return UpdateProductVariant(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            variant = ProductVariant.objects.get(id=id)
        except ProductVariant.DoesNotExist:
            return UpdateProductVariant(
                success=False,
                message="Product variant not found"
            )
        
        # Check SKU uniqueness if being updated
        if 'sku' in kwargs and kwargs['sku'] != variant.sku:
            if ProductVariant.objects.filter(sku=kwargs['sku']).exists():
                return UpdateProductVariant(
                    success=False,
                    message="SKU already exists"
                )
        
        # Update variant
        for field, value in kwargs.items():
            if field == 'attributes' and value is None:
                setattr(variant, field, {})
            else:
                setattr(variant, field, value)
        
        variant.save()
        
        return UpdateProductVariant(
            product_variant=variant,
            success=True,
            message="Product variant updated successfully"
        )


class DeleteProductVariant(Mutation):
    """
    Mutation to delete a ProductVariant
    """
    class Arguments:
        id = ID(required=True)
    
    success = Boolean()
    message = String()
    
    def mutate(self, info, id):
        if not info.context.user.is_authenticated:
            return DeleteProductVariant(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return DeleteProductVariant(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            variant = ProductVariant.objects.get(id=id)
            variant.delete()
            return DeleteProductVariant(
                success=True,
                message="Product variant deleted successfully"
            )
        except ProductVariant.DoesNotExist:
            return DeleteProductVariant(
                success=False,
                message="Product variant not found"
            )


# Shipping Mutations
class UpdateShippingPrices(Mutation):
    """
    Mutation to update shipping prices for a wilaya
    """
    class Arguments:
        wilaya_id = ID(required=True)
        stop_desk_price = Float(required=True)
        home_delivery_price = Float(required=True)
    
    shipping = Field(ShippingType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, wilaya_id, stop_desk_price, home_delivery_price):
        if not info.context.user.is_authenticated:
            return UpdateShippingPrices(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return UpdateShippingPrices(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            shipping = Shipping.objects.get(wilaya_id=wilaya_id)
            shipping.stop_desk_price = stop_desk_price
            shipping.home_delivery_price = home_delivery_price
            shipping.save()
            
            return UpdateShippingPrices(
                shipping=shipping,
                success=True,
                message="Shipping prices updated successfully"
            )
        except Shipping.DoesNotExist:
            return UpdateShippingPrices(
                success=False,
                message="Wilaya not found"
            )


class ToggleShippingStatus(Mutation):
    """
    Mutation to activate/deactivate shipping for a wilaya
    """
    class Arguments:
        wilaya_id = ID(required=True)
        is_active = Boolean(required=True)
    
    shipping = Field(ShippingType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, wilaya_id, is_active):
        if not info.context.user.is_authenticated:
            return ToggleShippingStatus(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return ToggleShippingStatus(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            shipping = Shipping.objects.get(wilaya_id=wilaya_id)
            shipping.is_active = is_active
            shipping.save()
            
            status_text = "activated" if is_active else "deactivated"
            return ToggleShippingStatus(
                shipping=shipping,
                success=True,
                message=f"Shipping for {shipping.name_ar} {status_text} successfully"
            )
        except Shipping.DoesNotExist:
            return ToggleShippingStatus(
                success=False,
                message="Wilaya not found"
            )


# Product Material Mutations
class AddMaterialToProduct(Mutation):
    """
    Mutation to add a material to a product
    """
    class Arguments:
        product_id = ID(required=True)
        material_id = ID(required=True)
        quantity_used = Float(default_value=1.0)
        unit = String(default_value='kg')
    
    product = Field(ProductType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, product_id, material_id, quantity_used=1.0, unit='kg'):
        if not info.context.user.is_authenticated:
            return AddMaterialToProduct(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return AddMaterialToProduct(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            product = Product.objects.get(id=product_id)
            material = Material.objects.get(id=material_id)
        except Product.DoesNotExist:
            return AddMaterialToProduct(
                success=False,
                message="Product not found"
            )
        except Material.DoesNotExist:
            return AddMaterialToProduct(
                success=False,
                message="Material not found"
            )
        
        # Check if relationship already exists
        if ProductMaterial.objects.filter(product=product, material=material).exists():
            return AddMaterialToProduct(
                success=False,
                message="Material already added to this product"
            )
        
        # Create the relationship
        ProductMaterial.objects.create(
            product=product,
            material=material,
            quantity_used=quantity_used,
            unit=unit
        )
        
        return AddMaterialToProduct(
            product=product,
            success=True,
            message="Material added to product successfully"
        )


class RemoveMaterialFromProduct(Mutation):
    """
    Mutation to remove a material from a product
    """
    class Arguments:
        product_id = ID(required=True)
        material_id = ID(required=True)
    
    product = Field(ProductType)
    success = Boolean()
    message = String()
    
    def mutate(self, info, product_id, material_id):
        if not info.context.user.is_authenticated:
            return RemoveMaterialFromProduct(
                success=False,
                message="Authentication required"
            )
        
        if not info.context.user.is_staff:
            return RemoveMaterialFromProduct(
                success=False,
                message="Staff permissions required"
            )
        
        try:
            product = Product.objects.get(id=product_id)
            material = Material.objects.get(id=material_id)
        except Product.DoesNotExist:
            return RemoveMaterialFromProduct(
                success=False,
                message="Product not found"
            )
        except Material.DoesNotExist:
            return RemoveMaterialFromProduct(
                success=False,
                message="Material not found"
            )
        
        try:
            product_material = ProductMaterial.objects.get(
                product=product,
                material=material
            )
            product_material.delete()
            return RemoveMaterialFromProduct(
                product=product,
                success=True,
                message="Material removed from product successfully"
            )
        except ProductMaterial.DoesNotExist:
            return RemoveMaterialFromProduct(
                success=False,
                message="Material not found in this product"
            )


# Root Query
class Query(ObjectType, CartQuery, WishlistQuery, ReviewQuery, DesignQuery, NotificationQuery, SmartAlertQuery):
    """
    Root query for API models
    """
    # ProductVariant queries
    product_variant = relay.Node.Field(ProductVariantType)
    all_product_variants = DjangoFilterConnectionField(ProductVariantType)
    
    def resolve_active_organization(self, info):
        """
        Resolve the currently active organization
        """
        try:
            return Organization.objects.get(is_active=True)
        except Organization.DoesNotExist:
            return None
    
    def resolve_public_social_links(self, info):
        """
        Resolve all public social links from active organization
        """
        try:
            active_org = Organization.objects.get(is_active=True)
            return active_org.social_links.filter(
                is_active=True, 
                platform_type=PlatformType.PUBLIC
            ).order_by('order_index')
        except Organization.DoesNotExist:
            return Social.objects.none()
    
    # Product queries
    product = relay.Node.Field(ProductType)
    all_products = DjangoFilterConnectionField(ProductType)
    
    # Category queries
    category = relay.Node.Field(CategoryType)
    all_categories = DjangoFilterConnectionField(CategoryType)
    
    # Material queries
    material = relay.Node.Field(MaterialType)
    all_materials = DjangoFilterConnectionField(MaterialType)
    
    # Shipping queries
    shipping = relay.Node.Field(ShippingType)
    all_shipping = DjangoFilterConnectionField(ShippingType)
    active_shipping = DjangoFilterConnectionField(ShippingType, filter={'is_active': True})
    
    # User queries
    user = relay.Node.Field(UserType)
    all_users = DjangoFilterConnectionField(UserType)
    
    # UserProfile queries
    user_profile = relay.Node.Field(UserProfileType)
    all_user_profiles = DjangoFilterConnectionField(UserProfileType)
    
    # Organization queries
    organization = relay.Node.Field(OrganizationType)
    all_organizations = DjangoFilterConnectionField(OrganizationType)
    active_organization = Field(OrganizationType)
    
    # Social queries
    social = relay.Node.Field(SocialType)
    all_social = DjangoFilterConnectionField(SocialType)
    public_social_links = List(SocialType)
    
    # DesignCategory queries
    design_category = relay.Node.Field(DesignCategoryType)
    all_design_categories = DjangoFilterConnectionField(DesignCategoryType)
    categories = List(DesignCategoryType)
    
    def resolve_categories(self, info):
        """
        Resolve active design categories ordered by design_count (most designs first)
        """
        return DesignCategory.objects.filter(
            is_active=True
        ).order_by('-design_count')
    
    # Design queries
    design = relay.Node.Field(DesignType)
    all_designs = DjangoFilterConnectionField(DesignType)


# Root Mutation
class Mutation(ObjectType, CartMutation, WishlistMutation, ReviewMutation, DesignMutation, NotificationMutation, SmartAlertMutation):
    """
    Root mutation for API models
    """
    # ProductVariant mutations
    create_product_variant = CreateProductVariant.Field()
    update_product_variant = UpdateProductVariant.Field()
    delete_product_variant = DeleteProductVariant.Field()
    
    # Product Material mutations
    add_material_to_product = AddMaterialToProduct.Field()
    remove_material_from_product = RemoveMaterialFromProduct.Field()
    
    # Shipping mutations
    update_shipping_prices = UpdateShippingPrices.Field()
    toggle_shipping_status = ToggleShippingStatus.Field()


# Export for use in main schema
__all__ = [
    'Query',
    'Mutation',
    'ProductVariantType',
    'ProductType',
    'CategoryType',
    'MaterialType',
    'ShippingType',
    'ShippingMethodType',
    'ShippingPriceType',
    'UserType',
    'UserProfileType',
    'ProductImageType',
    'OrganizationType',
    'SocialType',
    'CartItemType',
    'WishlistType',
    'WishlistSettingsType',
    'ReviewType',
    'ReviewReportType',
    'DesignCategoryType',
    'DesignType',
]
