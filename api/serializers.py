"""
API Serializers Module for VynilArt API
This module provides serializers for all API models
"""
from rest_framework import serializers
from django.db import models
from .models import (
    User, UserProfile, Category, Material, Product, ProductImage, 
    ProductVariant, ProductMaterial, Shipping, ShippingMethod, ShippingPrice,
    Order, OrderItem, OrderTimeline, Payment, Coupon, CartItem, PromotionCoupon, 
    CouponUsage, CouponCampaign, Wishlist, WishlistSettings, 
    Alert, AlertRule, Review, ReviewReport, DesignCategory, 
    Design, Notification, ErpNextSyncLog, BehaviorTracking, 
    Forecast, CustomerSegment, CustomerSegmentUsers, PricingEngine, 
    BlogCategory, BlogPost, ConversationHistory, DashboardSettings
)


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer with common fields
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProductVariantSerializer(BaseSerializer):
    """
    Serializer for ProductVariant model with JSON field handling
    """
    class Meta:
        model = ProductVariant
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    # Handle JSON field properly
    attributes = serializers.JSONField(default=dict)
    
    def validate_attributes(self, value):
        """
        Validate attributes JSON field
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Attributes must be a dictionary")
        return value
    
    def validate_sku(self, value):
        """
        Validate SKU uniqueness
        """
        if self.instance and self.instance.sku == value:
            return value
        
        if ProductVariant.objects.filter(sku=value).exists():
            raise serializers.ValidationError("SKU must be unique")
        return value
    
    def validate_price(self, value):
        """
        Validate price is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock(self, value):
        """
        Validate stock is non-negative
        """
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


class ProductSerializer(BaseSerializer):
    """
    Serializer for Product model with variants and materials
    """
    variants = ProductVariantSerializer(many=True, read_only=True)
    materials = MaterialSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(BaseSerializer):
    """
    Serializer for Category model
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """
        Get child categories
        """
        return CategorySerializer(obj.children.all(), many=True).data


class MaterialSerializer(BaseSerializer):
    """
    Serializer for Material model
    """
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingSerializer(BaseSerializer):
    """
    Serializer for Shipping model
    """
    class Meta:
        model = Shipping
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingMethodSerializer(BaseSerializer):
    """
    Serializer for ShippingMethod model
    """
    class Meta:
        model = ShippingMethod
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingPriceSerializer(BaseSerializer):
    """
    Serializer for ShippingPrice model
    """
    class Meta:
        model = ShippingPrice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductImageSerializer(BaseSerializer):
    """
    Serializer for ProductImage model
    """
    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'password', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def create(self, validated_data):
        """
        Create user with encrypted password
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(BaseSerializer):
    """
    Serializer for UserProfile model
    """
    user = UserSerializer(read_only=True)
    preferences = serializers.JSONField(default=dict)
    settings = serializers.JSONField(default=dict)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# Additional serializers for other models can be added here
# For now, focusing on ProductVariant as requested

__all__ = [
    'ProductVariantSerializer',
    'ProductSerializer',
    'CategorySerializer',
    'MaterialSerializer',
    'ShippingSerializer',
    'ShippingMethodSerializer',
    'ShippingPriceSerializer',
    'ProductImageSerializer',
    'UserSerializer',
    'UserProfileSerializer',
]
