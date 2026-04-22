from graphene import relay, ObjectType, Schema, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

# Import all new schemas from api package individually to avoid circular import
from api.schema.user_schema import UserQuery, UserMutation
from api.schema.product_schema import ProductQuery, ProductMutation
from api.schema.cart_schema import CartQuery, CartMutation
from api.schema.wishlist_schema import WishlistQuery, WishlistMutation
from api.schema.review_schema import ReviewQuery, ReviewMutation
from api.schema.design_schema import DesignQuery, DesignMutation
from api.schema.notification_schema import NotificationQuery, NotificationMutation
from api.schema.smart_alert_schema import SmartAlertQuery, SmartAlertMutation
from api.schema.interaction_schema import InteractionQuery
from api.schema.content_schema import ContentQuery
from api.schema.system_schema import SystemQuery
from api.schema.alert_schema import AlertQuery
from api.schema.organization_schema import OrganizationQuery, OrganizationMutation
from api.schema.payment_method_schema import PaymentMethodQuery
from api.schema.analytics_schema import AnalyticsQuery
from api.schema.shipping_schema import ShippingQuery, ShippingMutation
from api.schema.order_schema import OrderQuery, OrderMutation
from api.schema.coupon_schema import CouponQuery, CouponMutation

# New schema imports for missing models
from api.schema.blog_schema import BlogQuery, BlogMutation
from api.schema.promotion_schema import PromotionQuery, PromotionMutation
from api.schema.erpnext_schema import ERPNextQuery, ERPNextMutation
from api.schema.conversation_schema import ConversationQuery, ConversationMutation
from api.schema.dashboard_schema import DashboardQuery, DashboardMutation

User = get_user_model()


# Authentication and Permission Mixins
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


# Combine all queries and mutations
class Query(UserQuery, ProductQuery, CartQuery, WishlistQuery, ReviewQuery, DesignQuery, NotificationQuery, SmartAlertQuery, InteractionQuery, ContentQuery, SystemQuery, AlertQuery, OrganizationQuery, PaymentMethodQuery, AnalyticsQuery, ShippingQuery, OrderQuery, CouponQuery, BlogQuery, PromotionQuery, ERPNextQuery, ConversationQuery, DashboardQuery):
    """Root query combining all domain queries"""
    pass

class Mutation(UserMutation, ProductMutation, CartMutation, WishlistMutation, ReviewMutation, DesignMutation, NotificationMutation, SmartAlertMutation, OrganizationMutation, ShippingMutation, OrderMutation, CouponMutation, BlogMutation, PromotionMutation, ERPNextMutation, ConversationMutation, DashboardMutation):
    """Root mutation combining all domain mutations"""
    pass

# Export schema
schema = Schema(query=Query, mutation=Mutation)
