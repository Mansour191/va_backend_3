"""
Shipping Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg
from decimal import Decimal
from api.models.shipping import Shipping, ShippingMethod, ShippingPrice
from api.models.organization import Organization
from api.schema.organization_schema import OrganizationObjectType


class ShippingType(DjangoObjectType):
    """Enhanced shipping type for Algerian wilayas"""
    id = graphene.ID(required=True)
    wilaya_id = String()
    wilaya_code = Int()
    name_ar = String()
    name_en = String()
    
    # Geographic and administrative info
    region = String()
    is_active = Boolean()
    is_metropolitan = Boolean()
    
    # Google Maps Integration
    pickup_latitude = Float()
    pickup_longitude = Float()
    radius_km = Int()
    maps_url = String()
    
    # Service availability
    home_delivery_available = Boolean()
    stop_desk_available = Boolean()
    express_available = Boolean()
    pickup_point_available = Boolean()
    
    # Organization integration
    base_city = Field(lambda: OrganizationObjectType)
    
    # Computed fields
    available_shipping_methods = List(lambda: ShippingMethodType)
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Shipping
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'wilaya_id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_fr': ['exact', 'icontains'],
            'is_active': ['exact'],
        }

    def resolve_available_shipping_methods(self, info):
        """Get available shipping methods for this wilaya"""
        return self.get_available_shipping_methods()


class ShippingMethodType(DjangoObjectType):
    """Shipping method type matching api_shipping_method table"""
    id = graphene.ID(required=True)
    name = String()
    provider_name = String()
    base_cost = Float()
    estimated_days = String()
    is_active = Boolean()
    description = String()
    
    # Organization relationship
    organization = Field(lambda: OrganizationObjectType)
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = ShippingMethod
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'provider_name': ['exact', 'icontains'],
            'is_active': ['exact'],
            'organization': ['exact'],
        }


class ShippingPriceType(DjangoObjectType):
    """Shipping price type"""
    id = graphene.ID(required=True)
    wilaya = Field(ShippingType)
    shipping_method = Field(ShippingMethodType)
    
    # Pricing for different service types
    home_delivery_price = Float()
    stop_desk_price = Float()
    express_price = Float()
    pickup_price = Float()
    
    # Additional pricing options
    free_shipping_minimum = Float()
    weight_surcharge = Float()
    volume_surcharge = Float()
    
    # Service level options
    cod_available = Boolean()
    cod_fee = Float()
    insurance_available = Boolean()
    insurance_rate = Float()
    tracking_available = Boolean()
    
    # Restrictions
    max_weight = Float()
    max_value = Float()
    
    # Validity period
    valid_from = graphene.Date()
    valid_to = graphene.Date()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = ShippingPrice
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'wilaya': ['exact'],
            'shipping_method': ['exact'],
            'is_active': ['exact'],
            'home_delivery_price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'stop_desk_price': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


# Input Types
class ShippingInput(graphene.InputObjectType):
    """Input for shipping creation and updates"""
    wilaya_id = String(required=True)
    wilaya_code = Int(required=True)
    name_ar = String(required=True)
    name_en = String(required=True)
    region = String()
    is_active = Boolean(default_value=True)
    is_metropolitan = Boolean(default_value=False)
    
    # Google Maps Integration
    pickup_latitude = Float()
    pickup_longitude = Float()
    radius_km = Int()
    maps_url = String()
    
    # Service availability
    home_delivery_available = Boolean(default_value=True)
    stop_desk_available = Boolean(default_value=True)
    express_available = Boolean(default_value=False)
    pickup_point_available = Boolean(default_value=False)


class ShippingMethodInput(graphene.InputObjectType):
    """Input for shipping method creation and updates"""
    name = String(required=True)
    provider_name = String()
    base_cost = Float(default_value=0.00)
    estimated_days = String()
    is_active = Boolean(default_value=True)
    description = String()
    organization_id = ID(required=True)


class ShippingPriceInput(graphene.InputObjectType):
    """Input for shipping price creation and updates"""
    wilaya_id = ID(required=True)
    shipping_method_id = ID(required=True)
    
    # Pricing for different service types
    home_delivery_price = Float(required=True)
    stop_desk_price = Float(required=True)
    express_price = Float()
    pickup_price = Float()
    
    # Additional pricing options
    free_shipping_minimum = Float()
    weight_surcharge = Float(default_value=0)
    volume_surcharge = Float(default_value=0)
    
    # Service level options
    cod_available = Boolean(default_value=True)
    cod_fee = Float(default_value=0)
    insurance_available = Boolean(default_value=False)
    insurance_rate = Float(default_value=0)
    tracking_available = Boolean(default_value=True)
    
    # Restrictions
    max_weight = Float()
    max_value = Float()
    
    # Validity period
    valid_from = graphene.Date()
    valid_to = graphene.Date()


# Mutations
class CreateShipping(Mutation):
    """Create a new shipping wilaya"""
    
    class Arguments:
        input = ShippingInput(required=True)

    success = Boolean()
    message = String()
    shipping = Field(ShippingType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            shipping = Shipping.objects.create(**input)
            
            return CreateShipping(
                success=True,
                message="Shipping created successfully",
                shipping=shipping
            )
            
        except Exception as e:
            return CreateShipping(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateShipping(Mutation):
    """Update an existing shipping wilaya"""
    
    class Arguments:
        id = ID(required=True)
        input = ShippingInput(required=True)

    success = Boolean()
    message = String()
    shipping = Field(ShippingType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            shipping = Shipping.objects.get(id=id)
            
            for field, value in input.items():
                if hasattr(shipping, field):
                    setattr(shipping, field, value)
            
            shipping.save()
            
            return UpdateShipping(
                success=True,
                message="Shipping updated successfully",
                shipping=shipping
            )
            
        except Shipping.DoesNotExist:
            return UpdateShipping(
                success=False,
                message="Shipping not found",
                errors=["Shipping not found"]
            )
        except Exception as e:
            return UpdateShipping(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateShippingMethod(Mutation):
    """Create a new shipping method"""
    
    class Arguments:
        input = ShippingMethodInput(required=True)

    success = Boolean()
    message = String()
    shipping_method = Field(ShippingMethodType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.organization import Organization
            
            # Get organization
            organization = Organization.objects.get(id=input['organization_id'])
            
            # Create shipping method without organization_id from input
            shipping_method_data = {k: v for k, v in input.items() if k != 'organization_id'}
            shipping_method = ShippingMethod.objects.create(
                organization=organization,
                **shipping_method_data
            )
            
            return CreateShippingMethod(
                success=True,
                message="Shipping method created successfully",
                shipping_method=shipping_method
            )
            
        except Organization.DoesNotExist:
            return CreateShippingMethod(
                success=False,
                message="Organization not found",
                errors=["Organization not found"]
            )
        except Exception as e:
            return CreateShippingMethod(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateShippingMethod(Mutation):
    """Update an existing shipping method"""
    
    class Arguments:
        id = ID(required=True)
        input = ShippingMethodInput(required=True)

    success = Boolean()
    message = String()
    shipping_method = Field(ShippingMethodType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            shipping_method = ShippingMethod.objects.get(id=id)
            
            for field, value in input.items():
                if hasattr(shipping_method, field):
                    setattr(shipping_method, field, value)
            
            shipping_method.save()
            
            return UpdateShippingMethod(
                success=True,
                message="Shipping method updated successfully",
                shipping_method=shipping_method
            )
            
        except ShippingMethod.DoesNotExist:
            return UpdateShippingMethod(
                success=False,
                message="Shipping method not found",
                errors=["Shipping method not found"]
            )
        except Exception as e:
            return UpdateShippingMethod(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateShippingPrice(Mutation):
    """Create a new shipping price"""
    
    class Arguments:
        input = ShippingPriceInput(required=True)

    success = Boolean()
    message = String()
    shipping_price = Field(ShippingPriceType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.shipping import Shipping, ShippingMethod
            
            wilaya = Shipping.objects.get(id=input['wilaya_id'])
            shipping_method = ShippingMethod.objects.get(id=input['shipping_method_id'])
            
            shipping_price = ShippingPrice.objects.create(
                wilaya=wilaya,
                shipping_method=shipping_method,
                **{k: v for k, v in input.items() if k not in ['wilaya_id', 'shipping_method_id']}
            )
            
            return CreateShippingPrice(
                success=True,
                message="Shipping price created successfully",
                shipping_price=shipping_price
            )
            
        except Exception as e:
            return CreateShippingPrice(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ShippingQuery(ObjectType):
    """Shipping queries"""
    
    shipping = List(ShippingType)
    shipping_wilaya = Field(ShippingType, id=ID(required=True))
    shipping_connection = DjangoFilterConnectionField(ShippingType)
    
    shipping_methods = List(ShippingMethodType)
    shipping_method = Field(ShippingMethodType, id=ID(required=True))
    shipping_methods_connection = DjangoFilterConnectionField(ShippingMethodType)
    shipping_methods_by_organization = List(ShippingMethodType, organization_id=ID(required=True))
    
    shipping_prices = List(ShippingPriceType)
    shipping_price = Field(ShippingPriceType, id=ID(required=True))
    shipping_prices_connection = DjangoFilterConnectionField(ShippingPriceType)
    
    def resolve_shipping(self, info):
        """Get all shipping wilayas"""
        return Shipping.objects.all()
    
    def resolve_shipping_wilaya(self, info, id):
        """Get shipping wilaya by ID"""
        try:
            return Shipping.objects.get(id=id)
        except Shipping.DoesNotExist:
            return None
    
    def resolve_shipping_methods(self, info):
        """Get all shipping methods"""
        return ShippingMethod.objects.select_related('organization').all()
    
    def resolve_shipping_method(self, info, id):
        """Get shipping method by ID"""
        try:
            return ShippingMethod.objects.select_related('organization').get(id=id)
        except ShippingMethod.DoesNotExist:
            return None
    
    def resolve_shipping_methods_by_organization(self, info, organization_id):
        """Get shipping methods by organization_id"""
        try:
            from api.models.organization import Organization
            organization = Organization.objects.get(id=organization_id)
            return ShippingMethod.objects.filter(organization=organization, is_active=True)
        except Organization.DoesNotExist:
            return []
    
    def resolve_shipping_prices(self, info):
        """Get all shipping prices"""
        return ShippingPrice.objects.select_related('wilaya', 'shipping_method').all()
    
    def resolve_shipping_price(self, info, id):
        """Get shipping price by ID"""
        try:
            return ShippingPrice.objects.select_related('wilaya', 'shipping_method').get(id=id)
        except ShippingPrice.DoesNotExist:
            return None


# Mutation Class
class ShippingMutation(ObjectType):
    """Shipping mutations"""
    
    create_shipping = CreateShipping.Field()
    update_shipping = UpdateShipping.Field()
    create_shipping_method = CreateShippingMethod.Field()
    update_shipping_method = UpdateShippingMethod.Field()
    create_shipping_price = CreateShippingPrice.Field()
