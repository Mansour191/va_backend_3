"""
Basic admin registration for missing API models - no field configurations
"""

from django.contrib import admin

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

# ==================== BASIC ADMIN REGISTRATIONS ====================

admin.site.register(AlertRule)
admin.site.register(CustomerSegmentUser)
admin.site.register(SmartAlert)
admin.site.register(CouponCampaign)
admin.site.register(CouponUsage)
admin.site.register(PromotionCoupon)
admin.site.register(PromotionCouponUsage)
admin.site.register(OrderItem)
admin.site.register(OrderTimeline)
admin.site.register(ProductImage)
admin.site.register(ProductMaterial)
admin.site.register(ProductVariant)
admin.site.register(ShippingMethod)
admin.site.register(ShippingPrice)
admin.site.register(UserProfileBeforeUpdate)
