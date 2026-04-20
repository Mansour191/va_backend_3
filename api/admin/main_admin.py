"""
Main admin configuration for API models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
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

# ==================== ANALYTICS & TRACKING ====================

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    """Admin configuration for Alert Rules"""
    
    list_display = ['name', 'alert_type', 'priority', 'is_active', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'alert_type', 'priority')
        }),
        ('Rule Configuration', {
            'fields': ('conditions', 'actions', 'threshold_value')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomerSegmentUser)
class CustomerSegmentUserAdmin(admin.ModelAdmin):
    """Admin configuration for Customer Segment User relationship"""
    
    list_display = ['user', 'customer_segment', 'assigned_at', 'is_active']
    list_filter = ['customer_segment', 'is_active', 'assigned_at']
    search_fields = ['user__username', 'user__email', 'customer_segment__name']
    readonly_fields = ['assigned_at']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('user', 'customer_segment', 'is_active')
        }),
        ('Metadata', {
            'fields': ('assigned_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SmartAlert)
class SmartAlertAdmin(admin.ModelAdmin):
    """Admin configuration for Smart Alerts"""
    
    list_display = ['title', 'alert_type', 'priority', 'user', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_resolved', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('title', 'message', 'alert_type', 'priority')
        }),
        ('Target', {
            'fields': ('user', 'target_type', 'target_id')
        }),
        ('Status', {
            'fields': ('is_resolved', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ==================== COUPON & PROMOTION ====================

@admin.register(CouponCampaign)
class CouponCampaignAdmin(admin.ModelAdmin):
    """Admin configuration for Coupon Campaigns"""
    
    list_display = ['name', 'start_date', 'end_date', 'budget', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date', 'end_date', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'description', 'start_date', 'end_date')
        }),
        ('Budget', {
            'fields': ('budget', 'currency')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Admin configuration for Coupon Usage tracking"""
    
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['coupon', 'used_at']
    search_fields = ['coupon__code', 'user__username', 'order__order_number']
    readonly_fields = ['used_at']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('coupon', 'user', 'order', 'discount_amount')
        }),
        ('Metadata', {
            'fields': ('used_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromotionCoupon)
class PromotionCouponAdmin(admin.ModelAdmin):
    """Admin configuration for Promotion Coupons"""
    
    list_display = ['code', 'campaign', 'discount_type', 'discount_value', 'is_active', 'created_at']
    list_filter = ['discount_type', 'is_active', 'campaign', 'created_at']
    search_fields = ['code', 'campaign__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'campaign', 'name', 'description')
        }),
        ('Discount Configuration', {
            'fields': ('discount_type', 'discount_value', 'minimum_order_amount')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit_per_user', 'usage_limit_total', 'used_count')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromotionCouponUsage)
class PromotionCouponUsageAdmin(admin.ModelAdmin):
    """Admin configuration for Promotion Coupon Usage"""
    
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['coupon', 'used_at']
    search_fields = ['coupon__code', 'user__username', 'order__order_number']
    readonly_fields = ['used_at']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('coupon', 'user', 'order', 'discount_amount')
        }),
        ('Metadata', {
            'fields': ('used_at',),
            'classes': ('collapse',)
        }),
    )

# ==================== ORDER MANAGEMENT ====================

class OrderItemInline(admin.TabularInline):
    """Inline for Order Items in Order admin"""
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    
    fields = (
        'product', 'quantity', 'unit_price', 'total_price',
        'created_at', 'updated_at'
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for Order Items"""
    
    list_display = ['order', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['order__status', 'created_at', 'product']
    search_fields = ['order__order_number', 'product__name_ar', 'product__name_en']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'product')
        }),
        ('Pricing', {
            'fields': ('quantity', 'unit_price', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderTimeline)
class OrderTimelineAdmin(admin.ModelAdmin):
    """Admin configuration for Order Timeline"""
    
    list_display = ['order', 'status', 'timestamp', 'comment']
    list_filter = ['status', 'timestamp']
    search_fields = ['order__order_number', 'comment']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Timeline Information', {
            'fields': ('order', 'status', 'comment')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

# ==================== PRODUCT MANAGEMENT ====================

class ProductImageInline(admin.TabularInline):
    """Inline for Product Images in Product admin"""
    model = ProductImage
    extra = 1
    readonly_fields = ['created_at']
    
    fields = (
        'image', 'alt_text', 'is_primary', 'order_index',
        'created_at'
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for Product Images"""
    
    list_display = ['product', 'image_preview', 'is_primary', 'order_index', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name_ar', 'product__name_en', 'alt_text']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('product', 'image', 'alt_text')
        }),
        ('Display Settings', {
            'fields': ('is_primary', 'order_index')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Show image preview in admin list"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.image.url
            )
        return mark_safe('<span style="color: #999;">No Image</span>')
    image_preview.short_description = _('Preview')
    image_preview.allow_tags = True


@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    """Admin configuration for Product-Material relationship"""
    
    list_display = ['product', 'material', 'quantity_required', 'created_at']
    list_filter = ['material', 'created_at']
    search_fields = ['product__name_ar', 'product__name_en', 'material__name_ar', 'material__name_en']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('product', 'material', 'quantity_required')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for Product Variants"""
    
    list_display = ['product', 'name', 'sku', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name_ar', 'product__name_en', 'name', 'sku']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Variant Information', {
            'fields': ('product', 'name', 'sku', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'cost')
        }),
        ('Inventory', {
            'fields': ('stock', 'weight', 'dimensions')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ==================== SHIPPING ====================

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """Admin configuration for Shipping Methods"""
    
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'organization']
    search_fields = ['name', 'organization__name_ar', 'organization__name_en']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Method Information', {
            'fields': ('organization', 'name', 'description')
        }),
        ('Configuration', {
            'fields': ('delivery_time', 'tracking_available')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShippingPrice)
class ShippingPriceAdmin(admin.ModelAdmin):
    """Admin configuration for Shipping Prices"""
    
    list_display = ['wilaya', 'shipping_method', 'stop_desk_price', 'home_delivery_price', 'is_active']
    list_filter = ['shipping_method', 'is_active']
    search_fields = ['wilaya__name_ar', 'wilaya__name_fr', 'shipping_method__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Price Configuration', {
            'fields': ('wilaya', 'shipping_method', 'stop_desk_price', 'home_delivery_price')
        }),
        ('Additional Costs', {
            'fields': ('weight_surcharge', 'volume_surcharge')
        }),
        ('Options', {
            'fields': ('cod_available', 'cod_fee', 'insurance_available', 'insurance_rate')
        }),
        ('Limits', {
            'fields': ('max_weight', 'max_value')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ==================== SYSTEM ====================

@admin.register(UserProfileBeforeUpdate)
class UserProfileBeforeUpdateAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile Before Update (Audit)"""
    
    list_display = ['user', 'field_name', 'old_value_preview', 'new_value_preview', 'updated_at']
    list_filter = ['field_name', 'updated_at']
    search_fields = ['user__username', 'field_name']
    readonly_fields = ['user', 'field_name', 'old_value', 'new_value', 'updated_at']
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('user', 'field_name')
        }),
        ('Values', {
            'fields': ('old_value', 'new_value')
        }),
        ('Timestamp', {
            'fields': ('updated_at',)
        }),
    )
    
    def old_value_preview(self, obj):
        """Show preview of old value"""
        value = str(obj.old_value)
        return value[:50] + '...' if len(value) > 50 else value
    old_value_preview.short_description = _('Old Value')
    
    def new_value_preview(self, obj):
        """Show preview of new value"""
        value = str(obj.new_value)
        return value[:50] + '...' if len(value) > 50 else value
    new_value_preview.short_description = _('New Value')


# ==================== INLINE CONFIGURATIONS ====================

# Add inlines to existing admin classes
from core.admin import ProductAdmin, OrderAdmin

# Extend ProductAdmin with ProductImage and ProductVariant inlines
ProductAdmin.inlines.extend([ProductImageInline])

# Extend OrderAdmin with OrderItem and OrderTimeline inlines  
OrderAdmin.inlines.extend([OrderItemInline])
