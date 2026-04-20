"""
Simplified admin configuration for missing API models
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import (
    # Analytics & Tracking
    AlertRule, CustomerSegmentUser, SmartAlert,
    
    # Coupon & Promotion
    PromotionCoupon,
    
    # Order Management
    OrderItem, OrderTimeline,
    
    # Product Management
    ProductImage, ProductMaterial, ProductVariant,
    
    # Shipping
    ShippingMethod, ShippingPrice,
)

# Import models that aren't in __init__.py directly
from ..models.coupon import CouponUsage
from ..models.promotion import CouponCampaign, PromotionCouponUsage
from ..models.user import UserProfileBeforeUpdate

# ==================== SIMPLE ADMIN REGISTRATIONS ====================

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CustomerSegmentUser)
class CustomerSegmentUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at']

@admin.register(SmartAlert)
class SmartAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at']

@admin.register(CouponCampaign)
class CouponCampaignAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'used_at']
    readonly_fields = ['used_at']

@admin.register(PromotionCoupon)
class PromotionCouponAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PromotionCouponUsage)
class PromotionCouponUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'used_at']
    readonly_fields = ['used_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OrderTimeline)
class OrderTimelineAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp']
    readonly_fields = ['timestamp']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at']

@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ShippingPrice)
class ShippingPriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserProfileBeforeUpdate)
class UserProfileBeforeUpdateAdmin(admin.ModelAdmin):
    list_display = ['id', 'updated_at']
    readonly_fields = ['updated_at']
