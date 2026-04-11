"""
GraphQL Schema for Payment Method models
Updated to include payment methods with multilingual support and account details
"""

import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field_with_choices
from django.contrib.auth import get_user_model

from ..models.payment_method import PaymentMethod


User = get_user_model()


class UserObjectType(DjangoObjectType):
    """
    GraphQL type for User model
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class PaymentMethodObjectType(DjangoObjectType):
    """
    GraphQL type for Payment Method with all fields
    """
    name = graphene.String()
    instructions = graphene.String()
    display_icon = graphene.String()
    safe_account_number = graphene.String()
    fees_for_amount = graphene.JSONString()
    is_available_for_amount = graphene.Boolean()
    
    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'name_ar', 'name_en', 'name',
            'payment_type', 'gateway_provider',
            'account_name', 'account_number', 'iban',
            'instructions_ar', 'instructions_en', 'instructions',
            'icon', 'logo', 'display_icon',
            'order_index', 'is_active', 'is_default',
            'max_amount', 'fee_percentage', 'fee_fixed',
            'safe_account_number',
            'created_by', 'created_by_user', 'created_at', 'updated_at'
        )
    
    def resolve_name(self, info):
        """
        Resolve name based on request language
        """
        language = info.context.headers.get('Accept-Language', 'ar').split(',')[0].split('-')[0]
        return self.get_name(language)
    
    def resolve_instructions(self, info):
        """
        Resolve instructions based on request language
        """
        language = info.context.headers.get('Accept-Language', 'ar').split(',')[0].split('-')[0]
        return self.get_instructions(language)
    
    def resolve_display_icon(self, info):
        """
        Resolve Font Awesome icon class
        """
        return self.get_display_icon()
    
    def resolve_safe_account_number(self, info):
        """
        Resolve masked account number
        """
        return self.get_safe_account_number()
    
    def resolve_fees_for_amount(self, info):
        """
        Calculate fees for a sample amount (1000 DZD)
        """
        sample_amount = 1000
        return self.calculate_fees(sample_amount)
    
    def resolve_is_available_for_amount(self, info):
        """
        Check availability for sample amount
        """
        sample_amount = 1000
        return self.is_available_for_amount(sample_amount)
    
    def resolve_created_by_user(self, info):
        """
        Resolve user who created the payment method
        """
        return self.created_by


class PaymentMethodQuery(graphene.ObjectType):
    """
    GraphQL queries for Payment Methods
    """
    payment_methods = graphene.List(PaymentMethodObjectType)
    active_payment_methods = graphene.List(PaymentMethodObjectType)
    payment_method = graphene.Field(PaymentMethodObjectType, id=graphene.ID())
    default_payment_method = graphene.Field(PaymentMethodObjectType)
    
    def resolve_payment_methods(self, info):
        """
        Get all payment methods (for admin)
        """
        # Check if user is authenticated and is staff/admin
        if not info.context.user.is_authenticated:
            raise Exception('Authentication required')
        
        if not info.context.user.is_staff:
            raise Exception('Admin access required')
        
        return PaymentMethod.objects.get_all_methods()
    
    def resolve_active_payment_methods(self, info):
        """
        Get only active payment methods (for customers)
        """
        return PaymentMethod.objects.get_active_methods()
    
    def resolve_payment_method(self, info, id):
        """
        Get specific payment method by ID
        """
        try:
            # For public methods, allow access
            method = PaymentMethod.objects.get(pk=id)
            
            # If method is not active, only allow admin/staff access
            if not method.is_active and not (info.context.user.is_authenticated and info.context.user.is_staff):
                raise Exception('Payment method not available')
            
            return method
        except PaymentMethod.DoesNotExist:
            raise Exception('Payment method not found')
    
    def resolve_default_payment_method(self, info):
        """
        Get default payment method
        """
        try:
            return PaymentMethod.objects.get(is_default=True, is_active=True)
        except PaymentMethod.DoesNotExist:
            return None


class CreatePaymentMethod(graphene.Mutation):
    """
    GraphQL mutation to create payment method
    """
    class Arguments:
        name_ar = graphene.String(required=True)
        name_en = graphene.String(required=True)
        payment_type = graphene.String(required=True)
        gateway_provider = graphene.String(required=False)
        account_name = graphene.String(required=False)
        account_number = graphene.String(required=False)
        iban = graphene.String(required=False)
        instructions_ar = graphene.String(required=False)
        instructions_en = graphene.String(required=False)
        icon = graphene.String(required=False)
        order_index = graphene.Int(required=False, default_value=0)
        is_active = graphene.Boolean(required=False, default_value=True)
        is_default = graphene.Boolean(required=False, default_value=False)
        max_amount = graphene.Decimal(required=False)
        fee_percentage = graphene.Decimal(required=False, default_value=0)
        fee_fixed = graphene.Decimal(required=False, default_value=0)
    
    success = graphene.Boolean()
    message = graphene.String()
    payment_method = graphene.Field(PaymentMethodObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Create new payment method
        """
        # Check if user is authenticated and is staff/admin
        if not info.context.user.is_authenticated:
            return CreatePaymentMethod(
                success=False,
                message='Authentication required'
            )
        
        if not info.context.user.is_staff:
            return CreatePaymentMethod(
                success=False,
                message='Admin access required'
            )
        
        try:
            payment_method = PaymentMethod.objects.create(
                created_by=info.context.user,
                **kwargs
            )
            
            return CreatePaymentMethod(
                success=True,
                message='تم إضافة طريقة الدفع بنجاح',
                payment_method=payment_method
            )
            
        except Exception as e:
            return CreatePaymentMethod(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class UpdatePaymentMethod(graphene.Mutation):
    """
    GraphQL mutation to update payment method
    """
    class Arguments:
        id = graphene.ID(required=True)
        name_ar = graphene.String(required=False)
        name_en = graphene.String(required=False)
        payment_type = graphene.String(required=False)
        gateway_provider = graphene.String(required=False)
        account_name = graphene.String(required=False)
        account_number = graphene.String(required=False)
        iban = graphene.String(required=False)
        instructions_ar = graphene.String(required=False)
        instructions_en = graphene.String(required=False)
        icon = graphene.String(required=False)
        order_index = graphene.Int(required=False)
        is_active = graphene.Boolean(required=False)
        is_default = graphene.Boolean(required=False)
        max_amount = graphene.Decimal(required=False)
        fee_percentage = graphene.Decimal(required=False)
        fee_fixed = graphene.Decimal(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()
    payment_method = graphene.Field(PaymentMethodObjectType)
    
    def mutate(self, info, **kwargs):
        """
        Update existing payment method
        """
        # Check if user is authenticated and is staff/admin
        if not info.context.user.is_authenticated:
            return UpdatePaymentMethod(
                success=False,
                message='Authentication required'
            )
        
        if not info.context.user.is_staff:
            return UpdatePaymentMethod(
                success=False,
                message='Admin access required'
            )
        
        try:
            payment_method = PaymentMethod.objects.get(pk=kwargs.pop('id'))
            
            for field, value in kwargs.items():
                if value is not None:
                    setattr(payment_method, field, value)
            
            payment_method.save()
            
            return UpdatePaymentMethod(
                success=True,
                message='تم تحديث طريقة الدفع بنجاح',
                payment_method=payment_method
            )
            
        except PaymentMethod.DoesNotExist:
            return UpdatePaymentMethod(
                success=False,
                message='طريقة الدفع غير موجودة'
            )
        except Exception as e:
            return UpdatePaymentMethod(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class DeletePaymentMethod(graphene.Mutation):
    """
    GraphQL mutation to delete payment method
    """
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        """
        Delete payment method
        """
        # Check if user is authenticated and is staff/admin
        if not info.context.user.is_authenticated:
            return DeletePaymentMethod(
                success=False,
                message='Authentication required'
            )
        
        if not info.context.user.is_staff:
            return DeletePaymentMethod(
                success=False,
                message='Admin access required'
            )
        
        try:
            payment_method = PaymentMethod.objects.get(pk=id)
            
            # Prevent deletion of default payment method
            if payment_method.is_default:
                return DeletePaymentMethod(
                    success=False,
                    message='لا يمكن حذف طريقة الدفع الافتراضية'
                )
            
            payment_method.delete()
            
            return DeletePaymentMethod(
                success=True,
                message='تم حذف طريقة الدفع بنجاح'
            )
            
        except PaymentMethod.DoesNotExist:
            return DeletePaymentMethod(
                success=False,
                message='طريقة الدفع غير موجودة'
            )
        except Exception as e:
            return DeletePaymentMethod(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class SetDefaultPaymentMethod(graphene.Mutation):
    """
    GraphQL mutation to set default payment method
    """
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    payment_method = graphene.Field(PaymentMethodObjectType)
    
    def mutate(self, info, id):
        """
        Set payment method as default
        """
        # Check if user is authenticated and is staff/admin
        if not info.context.user.is_authenticated:
            return SetDefaultPaymentMethod(
                success=False,
                message='Authentication required'
            )
        
        if not info.context.user.is_staff:
            return SetDefaultPaymentMethod(
                success=False,
                message='Admin access required'
            )
        
        try:
            payment_method = PaymentMethod.objects.get(pk=id)
            payment_method.is_default = True
            payment_method.save()
            
            return SetDefaultPaymentMethod(
                success=True,
                message='تم تعيين طريقة الدفع الافتراضية بنجاح',
                payment_method=payment_method
            )
            
        except PaymentMethod.DoesNotExist:
            return SetDefaultPaymentMethod(
                success=False,
                message='طريقة الدفع غير موجودة'
            )
        except Exception as e:
            return SetDefaultPaymentMethod(
                success=False,
                message=f'حدث خطأ: {str(e)}'
            )


class PaymentMethodMutation(graphene.ObjectType):
    """
    GraphQL mutations for Payment Methods
    """
    create_payment_method = CreatePaymentMethod.Field()
    update_payment_method = UpdatePaymentMethod.Field()
    delete_payment_method = DeletePaymentMethod.Field()
    set_default_payment_method = SetDefaultPaymentMethod.Field()


# Complete schema with payment method queries and mutations
schema = graphene.Schema(
    query=PaymentMethodQuery,
    mutation=PaymentMethodMutation
)
