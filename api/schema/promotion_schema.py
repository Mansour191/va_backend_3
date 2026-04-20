"""
Promotion Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg

from api.models.promotion import PromotionCoupon


class PromotionCouponType(DjangoObjectType):
    """Promotion coupon type"""
    # Relations
    applicable_products = List('api.schema.product_schema.ProductType')
    
    # Computed fields
    is_valid = Boolean()
    remaining_uses = Int()
    discount_percentage = Float()

    class Meta:
        model = PromotionCoupon
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'code': ['exact', 'icontains'],
            'discount_type': ['exact'],
            'is_active': ['exact'],
            'valid_from': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'valid_to': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_valid(self, info):
        """Check if coupon is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.valid_from and self.valid_from > now:
            return False
        
        if self.valid_to and self.valid_to < now:
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True

    def resolve_remaining_uses(self, info):
        """Get remaining uses for this coupon"""
        if self.usage_limit:
            return max(0, self.usage_limit - self.usage_count)
        return None

    def resolve_discount_percentage(self, info):
        """Get discount as percentage if applicable"""
        if self.discount_type == 'percentage':
            return float(self.discount_value)
        return None


# Input Types
class PromotionCouponInput(graphene.InputObjectType):
    """Input for promotion coupon creation and updates"""
    code = String(required=True)
    description_ar = String()
    description_en = String()
    discount_type = String(required=True)
    discount_value = Float(required=True)
    minimum_order_amount = Float()
    maximum_discount_amount = Float()
    usage_limit = Int()
    is_active = Boolean()
    starts_at = DateTime()
    ends_at = DateTime()


# Mutations
class CreatePromotionCoupon(Mutation):
    """Create a new promotion coupon"""
    
    class Arguments:
        input = PromotionCouponInput(required=True)

    success = Boolean()
    message = String()
    coupon = Field(PromotionCouponType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreatePromotionCoupon(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            coupon = PromotionCoupon.objects.create(**input)
            
            return CreatePromotionCoupon(
                success=True,
                message="Promotion coupon created successfully",
                coupon=coupon
            )
            
        except Exception as e:
            return CreatePromotionCoupon(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdatePromotionCoupon(Mutation):
    """Update an existing promotion coupon"""
    
    class Arguments:
        id = ID(required=True)
        input = PromotionCouponInput(required=True)

    success = Boolean()
    message = String()
    coupon = Field(PromotionCouponType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return UpdatePromotionCoupon(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            coupon = PromotionCoupon.objects.get(id=id)
            
            for field, value in input.items():
                if hasattr(coupon, field):
                    setattr(coupon, field, value)
            
            coupon.save()
            
            return UpdatePromotionCoupon(
                success=True,
                message="Promotion coupon updated successfully",
                coupon=coupon
            )
            
        except PromotionCoupon.DoesNotExist:
            return UpdatePromotionCoupon(
                success=False,
                message="Promotion coupon not found",
                errors=["Promotion coupon not found"]
            )
        except Exception as e:
            return UpdatePromotionCoupon(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ValidateCoupon(Mutation):
    """Validate a coupon code"""
    
    class Arguments:
        code = String(required=True)
        order_amount = Float()

    success = Boolean()
    message = String()
    coupon = Field(PromotionCouponType)
    discount_amount = Float()
    errors = List(String)

    def mutate(self, info, code, order_amount=None):
        try:
            coupon = PromotionCoupon.objects.get(code=code.upper())
            
            if not coupon.is_valid:
                return ValidateCoupon(
                    success=False,
                    message="Coupon is not valid or expired",
                    errors=["Coupon is not valid or expired"]
                )
            
            discount_amount = 0
            if order_amount and order_amount >= coupon.minimum_order_amount:
                if coupon.discount_type == 'percentage':
                    discount_amount = order_amount * (coupon.discount_value / 100)
                    if coupon.maximum_discount_amount:
                        discount_amount = min(discount_amount, coupon.maximum_discount_amount)
                else:  # fixed amount
                    discount_amount = coupon.discount_value
            
            return ValidateCoupon(
                success=True,
                message="Coupon is valid",
                coupon=coupon,
                discount_amount=discount_amount
            )
            
        except PromotionCoupon.DoesNotExist:
            return ValidateCoupon(
                success=False,
                message="Coupon not found",
                errors=["Coupon not found"]
            )
        except Exception as e:
            return ValidateCoupon(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class PromotionQuery(ObjectType):
    """Promotion queries"""
    
    promotion_coupons = List(PromotionCouponType)
    promotion_coupon = Field(PromotionCouponType, id=ID(required=True))
    applicable_products = List('api.schema.product_schema.ProductType')
    active_promotion_coupons = List(PromotionCouponType)
    valid_coupon = Field(PromotionCouponType, code=String(required=True))
    
    def resolve_promotion_coupons(self, info):
        """Get all promotion coupons (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return PromotionCoupon.objects.all().order_by('-created_at')
        return []
    
    def resolve_promotion_coupon(self, info, id):
        """Get promotion coupon by ID"""
        user = info.context.user
        try:
            coupon = PromotionCoupon.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return coupon
            return None
        except PromotionCoupon.DoesNotExist:
            return None
    
    def resolve_active_promotion_coupons(self, info):
        """Get active promotion coupons"""
        from django.utils import timezone
        now = timezone.now()
        return PromotionCoupon.objects.filter(
            is_active=True,
            starts_at__lte=now,
            ends_at__gte=now
        ).order_by('-created_at')
    
    def resolve_valid_coupon(self, info, code):
        """Get valid coupon by code"""
        try:
            coupon = PromotionCoupon.objects.get(code=code.upper())
            if coupon.is_valid:
                return coupon
            return None
        except PromotionCoupon.DoesNotExist:
            return None


# Mutation Class
class PromotionMutation(ObjectType):
    """Promotion mutations"""
    
    create_promotion_coupon = CreatePromotionCoupon.Field()
    update_promotion_coupon = UpdatePromotionCoupon.Field()
    validate_coupon = ValidateCoupon.Field()
