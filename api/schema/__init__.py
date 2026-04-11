"""
API Schema Package for VynilArt
Contains all GraphQL schemas organized by domain
"""

# User and Authentication Schema
from .user_schema import UserQuery as UserQuery, UserMutation as UserMutation

# Product and Catalog Schema
from .product_schema import (
    ProductQuery as ProductQuery, ProductMutation as ProductMutation,
    CategoryNode, MaterialNode, ProductNode, ProductImageNode, 
    ProductVariantNode, ProductMaterialNode
)

# Order and Payment Schema
from .order_schema import (
    OrderQuery as OrderQuery, OrderMutation as OrderMutation,
    ShippingNode, OrderNode, OrderItemNode, OrderTimelineNode, PaymentNode
)

# Shipping and Logistics Schema
from .shipping_schema import ShippingQuery as ShippingQuery, ShippingMutation as ShippingMutation

# Cart and Commerce Schema
from .cart_schema import (
    CartQuery as CartQuery, CartMutation as CartMutation,
    CartItemNode, CouponNode
)
from .coupon_schema import CouponQuery as CouponQuery, CouponMutation as CouponMutation

# Wishlist and Alert Schema
from .wishlist_schema import (
    WishlistQuery as WishlistQuery, WishlistMutation as WishlistMutation,
    WishlistNode, AlertNode
)
from .alert_schema import AlertQuery as AlertQuery, AlertMutation as AlertMutation

# Content and Media Schema
from .content_schema import (
    ContentQuery as ContentQuery, ContentMutation as ContentMutation,
    ReviewNode, ReviewReportNode, DesignCategoryNode, DesignNode,
    BlogCategoryNode, BlogPostNode, NotificationNode, ERPNextSyncLogNode,
    BehaviorTrackingNode, ForecastNode, CustomerSegmentNode, PricingEngineNode,
    ConversationHistoryNode, DashboardSettingsNode, WishlistSettingsNode
)

# User Interaction Schema
from .interaction_schema import InteractionQuery as InteractionQuery, InteractionMutation as InteractionMutation

# Analytics and Business Intelligence Schema
from .analytics_schema import AnalyticsQuery as AnalyticsQuery, AnalyticsMutation as AnalyticsMutation

# System and Integration Schema
from .system_schema import SystemQuery as SystemQuery, SystemMutation as SystemMutation

# Organization Schema
from .organization_schema import OrganizationQuery as OrganizationQuery, OrganizationMutation as OrganizationMutation

# Combine all queries
class Query(
    UserQuery,
    ProductQuery,
    OrderQuery,
    ShippingQuery,
    CartQuery,
    CouponQuery,
    WishlistQuery,
    AlertQuery,
    ContentQuery,
    InteractionQuery,
    AnalyticsQuery,
    SystemQuery,
    OrganizationQuery,
):
    """Root query combining all domain queries"""
    pass

# Combine all mutations
class Mutation(
    UserMutation,
    ProductMutation,
    OrderMutation,
    ShippingMutation,
    CartMutation,
    CouponMutation,
    WishlistMutation,
    AlertMutation,
    ContentMutation,
    InteractionMutation,
    AnalyticsMutation,
    SystemMutation,
    OrganizationMutation,
):
    """Root mutation combining all domain mutations"""
    pass

# Export schema
schema = graphene.Schema(query=Query, mutation=Mutation)
