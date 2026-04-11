"""
Enhanced Coupon GraphQL Schema

This module provides comprehensive GraphQL schema for coupon management with:
- Advanced validation and security
- Real-time application
- Usage tracking and statistics
- Admin management capabilities
"""

import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from graphql import GraphQLError
from ..models.coupon import Coupon, CouponUsage

User = get_user_model()


class CouponUsageType(DjangoObjectType):
    """GraphQL type for coupon usage tracking"""
    
    class Meta:
        model = CouponUsage
        fields = '__all__'
    
    user_name = graphene.String()
    coupon_code = graphene.String()
    order_number = graphene.String()
    
    def resolve_user_name(self, info):
        return self.user.username if self.user else None
    
    def resolve_coupon_code(self, info):
        return self.coupon.code if self.coupon else None
    
    def resolve_order_number(self, info):
        return self.order.order_number if self.order else None


class CouponObjectType(DjangoObjectType):
    """Enhanced GraphQL type for coupons with computed fields"""
    
    class Meta:
        model = Coupon
        fields = '__all__'
    
    # Computed fields
    remaining_uses = graphene.Int()
    is_expired = graphene.Boolean()
    is_upcoming = graphene.Boolean()
    user_usage_count = graphene.Int()
    formatted_discount = graphene.String()
    status = graphene.String()
    
    # Relations
    usage_history = graphene.List(CouponUsageType)
    
    def resolve_remaining_uses(self, info):
        return self.remaining_uses
    
    def resolve_is_expired(self, info):
        return self.is_expired
    
    def resolve_is_upcoming(self, info):
        return self.is_upcoming
    
    def resolve_user_usage_count(self, info):
        user = info.context.user
        if user and user.is_authenticated:
            return self.get_user_usage_count(user)
        return 0
    
    def resolve_formatted_discount(self, info):
        if self.discount_type == 'percentage':
            return f"{self.discount_value}%"
        else:
            return f"{self.discount_value:,} د.ج"
    
    def resolve_status(self, info):
        now = timezone.now()
        if not self.is_active:
            return "غير نشط"
        elif self.valid_from and now < self.valid_from:
            return "قادم"
        elif self.valid_to and now > self.valid_to:
            return "منتهي"
        elif self.usage_limit and self.used_count >= self.usage_limit:
            return "مستنفذ"
        else:
            return "نشط"
    
    def resolve_usage_history(self, info):
        user = info.context.user
        if user and user.is_authenticated and user.is_staff:
            return self.couponusage.all().order_by('-used_at')[:50]
        return []


class CouponQuery(graphene.ObjectType):
    """GraphQL queries for coupons"""
    
    # Public queries
    validate_coupon = graphene.Field(
        CouponObjectType,
        code=graphene.String(required=True),
        order_value=graphene.Float()
    )
    
    # Admin queries
    coupons = graphene.List(CouponObjectType)
    coupon = graphene.Field(CouponObjectType, id=graphene.ID())
    coupon_by_code = graphene.Field(CouponObjectType, code=graphene.String())
    coupon_statistics = graphene.JSONString()
    
    def resolve_validate_coupon(self, info, code, order_value=None):
        """Validate and return coupon if valid"""
        user = info.context.user
        
        try:
            coupon = Coupon.objects.get_coupon_by_code(code)
            if not coupon:
                raise GraphQLError(_('رمز الكوبون غير صحيح'))
            
            # Check validity
            is_valid, message = coupon.is_valid(user=user, order_value=order_value)
            if not is_valid:
                raise GraphQLError(message)
            
            return coupon
            
        except Coupon.DoesNotExist:
            raise GraphQLError(_('رمز الكوبون غير صحيح'))
        except Exception as e:
            raise GraphQLError(str(e))
    
    def resolve_coupons(self, info):
        """Get all coupons (admin only)"""
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        return Coupon.objects.all().order_by('-created_at')
    
    def resolve_coupon(self, info, id):
        """Get coupon by ID (admin only)"""
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        try:
            return Coupon.objects.get(id=id)
        except Coupon.DoesNotExist:
            raise GraphQLError(_('الكوبون غير موجود'))
    
    def resolve_coupon_by_code(self, info, code):
        """Get coupon by code (admin only)"""
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        coupon = Coupon.objects.get_coupon_by_code(code)
        if not coupon:
            raise GraphQLError(_('الكوبون غير موجود'))
        
        return coupon
    
    def resolve_coupon_statistics(self, info):
        """Get comprehensive coupon statistics (admin only)"""
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        stats = {
            'total_coupons': Coupon.objects.count(),
            'active_coupons': Coupon.objects.filter(is_active=True).count(),
            'expired_coupons': Coupon.objects.filter(
                valid_to__lt=timezone.now()
            ).count(),
            'total_usage': Coupon.objects.aggregate(
                total=models.Sum('used_count')
            )['total'] or 0,
            'most_used': Coupon.objects.order_by('-used_count').first(),
            'recent_usage': CouponUsage.objects.select_related('coupon', 'user').order_by('-used_at')[:10],
        }
        
        return stats


class ApplyCouponInput(graphene.InputObjectType):
    """Input type for applying coupon"""
    code = graphene.String(required=True)
    order_value = graphene.Float()


class ApplyCoupon(graphene.Mutation):
    """Apply coupon to current session/cart"""
    
    class Arguments:
        input = ApplyCouponInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    coupon = graphene.Field(CouponObjectType)
    discount_amount = graphene.Float()
    
    def mutate(self, info, input):
        user = info.context.user
        code = input.code.upper().strip()
        order_value = input.order_value
        
        try:
            # Get and validate coupon
            coupon = Coupon.objects.get_coupon_by_code(code)
            if not coupon:
                return ApplyCoupon(
                    success=False,
                    message=_('رمز الكوبون غير صحيح')
                )
            
            # Check validity
            is_valid, message = coupon.is_valid(user=user, order_value=order_value)
            if not is_valid:
                return ApplyCoupon(
                    success=False,
                    message=message
                )
            
            # Calculate discount
            discount_amount = coupon.calculate_discount(order_value)
            
            # Store coupon in session for checkout
            if hasattr(info.context, 'session'):
                info.context.session['applied_coupon'] = {
                    'code': coupon.code,
                    'discount_amount': float(discount_amount),
                    'discount_type': coupon.discount_type,
                    'applied_at': timezone.now().isoformat()
                }
            
            return ApplyCoupon(
                success=True,
                message=_('تم تطبيق الكوبون بنجاح'),
                coupon=coupon,
                discount_amount=float(discount_amount)
            )
            
        except Exception as e:
            return ApplyCoupon(
                success=False,
                message=str(e)
            )


class CreateCouponInput(graphene.InputObjectType):
    """Input type for creating coupons"""
    code = graphene.String()
    name = graphene.String()
    description = graphene.String()
    discount_type = graphene.String()
    discount_value = graphene.Float()
    max_discount = graphene.Float()
    usage_limit = graphene.Int()
    usage_limit_per_user = graphene.Int()
    min_order_value = graphene.Float()
    max_order_value = graphene.Float()
    valid_from = graphene.DateTime()
    valid_to = graphene.DateTime()
    is_active = graphene.Boolean()
    applicable_products = graphene.List(graphene.ID)
    applicable_categories = graphene.List(graphene.ID)


class CreateCoupon(graphene.Mutation):
    """Create new coupon (admin only)"""
    
    class Arguments:
        input = CreateCouponInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    coupon = graphene.Field(CouponObjectType)
    
    def mutate(self, info, input):
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        try:
            # Generate code if not provided
            if not input.get('code'):
                temp_coupon = Coupon()
                input['code'] = temp_coupon.generate_code()
            
            # Create coupon
            coupon = Coupon.objects.create(
                created_by=user,
                **input
            )
            
            return CreateCoupon(
                success=True,
                message=_('تم إنشاء الكوبون بنجاح'),
                coupon=coupon
            )
            
        except ValidationError as e:
            return CreateCoupon(
                success=False,
                message=str(e)
            )
        except Exception as e:
            return CreateCoupon(
                success=False,
                message=str(e)
            )


class UpdateCouponInput(graphene.InputObjectType):
    """Input type for updating coupons"""
    id = graphene.ID(required=True)
    code = graphene.String()
    name = graphene.String()
    description = graphene.String()
    discount_type = graphene.String()
    discount_value = graphene.Float()
    max_discount = graphene.Float()
    usage_limit = graphene.Int()
    usage_limit_per_user = graphene.Int()
    min_order_value = graphene.Float()
    max_order_value = graphene.Float()
    valid_from = graphene.DateTime()
    valid_to = graphene.DateTime()
    is_active = graphene.Boolean()


class UpdateCoupon(graphene.Mutation):
    """Update existing coupon (admin only)"""
    
    class Arguments:
        input = UpdateCouponInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    coupon = graphene.Field(CouponObjectType)
    
    def mutate(self, info, input):
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        try:
            coupon_id = input.pop('id')
            coupon = Coupon.objects.get(id=coupon_id)
            
            # Update fields
            for field, value in input.items():
                if hasattr(coupon, field):
                    setattr(coupon, field, value)
            
            coupon.full_clean()
            coupon.save()
            
            return UpdateCoupon(
                success=True,
                message=_('تم تحديث الكوبون بنجاح'),
                coupon=coupon
            )
            
        except Coupon.DoesNotExist:
            return UpdateCoupon(
                success=False,
                message=_('الكوبون غير موجود')
            )
        except ValidationError as e:
            return UpdateCoupon(
                success=False,
                message=str(e)
            )
        except Exception as e:
            return UpdateCoupon(
                success=False,
                message=str(e)
            )


class DeleteCoupon(graphene.Mutation):
    """Delete coupon (admin only)"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        user = info.context.user
        if not user or not user.is_authenticated or not user.is_staff:
            raise GraphQLError(_('صلاحيات المشرف مطلوبة'))
        
        try:
            coupon = Coupon.objects.get(id=id)
            coupon_code = coupon.code
            coupon.delete()
            
            return DeleteCoupon(
                success=True,
                message=_('تم حذف الكوبون بنجاح')
            )
            
        except Coupon.DoesNotExist:
            return DeleteCoupon(
                success=False,
                message=_('الكوبون غير موجود')
            )
        except Exception as e:
            return DeleteCoupon(
                success=False,
                message=str(e)
            )


class GenerateCouponCode(graphene.Mutation):
    """Generate random coupon code"""
    
    success = graphene.Boolean()
    code = graphene.String()
    
    def mutate(self, info):
        temp_coupon = Coupon()
        code = temp_coupon.generate_code()
        
        return GenerateCouponCode(
            success=True,
            code=code
        )


class CouponMutation(graphene.ObjectType):
    """GraphQL mutations for coupons"""
    
    # Customer mutations
    apply_coupon = ApplyCoupon.Field()
    
    # Admin mutations
    create_coupon = CreateCoupon.Field()
    update_coupon = UpdateCoupon.Field()
    delete_coupon = DeleteCoupon.Field()
    generate_coupon_code = GenerateCouponCode.Field()


# Complete schema
schema = graphene.Schema(
    query=CouponQuery,
    mutation=CouponMutation
)
