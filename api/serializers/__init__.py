"""
API Serializers Package for VynilArt
Contains all Django REST serializers organized by domain
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""

# User and Authentication Serializers
from .user_serializers import (
    UserSerializer, UserProfileSerializer,
    UserCreateSerializer, UserUpdateSerializer
)

# Product and Catalog Serializers
from .product_serializers import (
    CategorySerializer, MaterialSerializer, ProductSerializer,
    ProductImageSerializer, ProductVariantSerializer, ProductMaterialSerializer
)

# Order and Payment Serializers
from .order_serializers import (
    OrderSerializer, OrderItemSerializer, OrderTimelineSerializer, PaymentSerializer
)

# Shipping and Logistics Serializers
from .shipping_serializers import (
    ShippingSerializer, ShippingMethodSerializer, ShippingPriceSerializer
)

# Cart and Commerce Serializers
from .cart_serializers import CartItemSerializer
from .coupon_serializers import CouponSerializer

# Wishlist and Alert Serializers
from .wishlist_serializers import WishlistSerializer, WishlistSettingsSerializer
from .alert_serializers import AlertSerializer, AlertRuleSerializer

# Content and Media Serializers
from .content_serializers import (
    BlogCategorySerializer, BlogPostSerializer,
    DesignCategorySerializer, DesignSerializer
)

# User Interaction Serializers
from .interaction_serializers import (
    ReviewSerializer, ReviewReportSerializer,
    BehaviorTrackingSerializer, ConversationHistorySerializer
)

# Analytics and Business Intelligence Serializers
from .analytics_serializers import (
    ForecastSerializer, CustomerSegmentSerializer,
    PricingEngineSerializer, DashboardSettingsSerializer
)

# System and Integration Serializers
from .system_serializers import (
    NotificationSerializer, ERPNextSyncLogSerializer, SystemConfigurationSerializer
)

# Organization Serializers
from .organization_serializers import (
    OrganizationSerializer, SocialSerializer, PlatformTypeSerializer
)

# Export all serializers for easy access
__all__ = [
    # User serializers
    'UserSerializer', 'UserProfileSerializer',
    'UserCreateSerializer', 'UserUpdateSerializer',
    
    # Product serializers
    'CategorySerializer', 'MaterialSerializer', 'ProductSerializer',
    'ProductImageSerializer', 'ProductVariantSerializer', 'ProductMaterialSerializer',
    
    # Order serializers
    'OrderSerializer', 'OrderItemSerializer', 'OrderTimelineSerializer', 'PaymentSerializer',
    
    # Shipping serializers
    'ShippingSerializer', 'ShippingMethodSerializer', 'ShippingPriceSerializer',
    
    # Commerce serializers
    'CartItemSerializer', 'CouponSerializer',
    
    # Wishlist serializers
    'WishlistSerializer', 'WishlistSettingsSerializer',
    'AlertSerializer', 'AlertRuleSerializer',
    
    # Content serializers
    'BlogCategorySerializer', 'BlogPostSerializer',
    'DesignCategorySerializer', 'DesignSerializer',
    
    # Interaction serializers
    'ReviewSerializer', 'ReviewReportSerializer',
    'BehaviorTrackingSerializer', 'ConversationHistorySerializer',
    
    # Analytics serializers
    'ForecastSerializer', 'CustomerSegmentSerializer',
    'PricingEngineSerializer', 'DashboardSettingsSerializer',
    
    # System serializers
    'NotificationSerializer', 'ERPNextSyncLogSerializer', 'SystemConfigurationSerializer',
    
    # Organization serializers
    'OrganizationSerializer', 'SocialSerializer', 'PlatformTypeSerializer',
]
