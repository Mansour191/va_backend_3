"""
API Models Package for VynilArt
Contains all extracted models from SQL schema organized by domain
"""

# User and Authentication Models
from .user import User, UserProfile

# Product and Catalog Models
from .product import (
    Category, Material, Product, ProductImage, 
    ProductVariant, ProductMaterial
)

# Shipping and Logistics Models
from .shipping import Shipping, ShippingMethod, ShippingPrice

# Order and Payment Models
from .order import (
    Order, OrderItem, OrderTimeline, Payment
)
from .coupon import Coupon

# Cart and Commerce Models
from .cart import CartItem
from .promotion import PromotionCoupon

# Wishlist and Alert Models
from .wishlist import Wishlist, WishlistSettings
from .alert import Alert, AlertRule
from .smart_alert import SmartAlert

# Review and Design Models
from .review import (
    Review, ReviewReport, DesignCategory, Design
)

# Notification Models
from .notification import Notification

# ERPNext Integration Models
from .erpnext import ERPNextSyncLog

# AI and Analytics Models
from .analytics_new import (
    BehaviorTracking, Forecast, CustomerSegment, 
    CustomerSegmentUser, PricingEngine
)

# Blog Models
from .blog import BlogCategory, BlogPost

# Conversation Models
from .conversation import ConversationHistory

# Dashboard and Settings Models
from .dashboard import DashboardSettings

# Organization Models
from .organization import Organization, Social, PlatformType

# Export all models for easy access
__all__ = [
    # User models
    'User', 'UserProfile',
    
    # Product models
    'Category', 'Material', 'Product', 'ProductImage', 
    'ProductVariant', 'ProductMaterial',
    
    # Shipping models
    'Shipping', 'ShippingMethod', 'ShippingPrice',
    
    # Order models
    'Order', 'OrderItem', 'OrderTimeline', 'Payment', 'Coupon',
    
    # Commerce models
    'CartItem', 'PromotionCoupon',
    
    # Wishlist models
    'Wishlist', 'WishlistSettings', 'Alert', 'AlertRule', 'SmartAlert',
    
    # Review models
    'Review', 'ReviewReport', 'DesignCategory', 'Design',
    
    # Notification models
    'Notification',
    
    # ERPNext models
    'ERPNextSyncLog',
    
    # Analytics models
    'BehaviorTracking', 'Forecast', 'CustomerSegment', 
    'CustomerSegmentUser', 'PricingEngine',
    
    # Blog models
    'BlogCategory', 'BlogPost',
    
    # Conversation models
    'ConversationHistory',
    
    # Dashboard models
    'DashboardSettings',
    
    # Organization models
    'Organization', 'Social', 'PlatformType',
]
