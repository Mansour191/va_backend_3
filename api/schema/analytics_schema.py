"""
Analytics Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg, Sum
from decimal import Decimal
from graphene import Mutation as BaseMutation


class BehaviorTrackingType(DjangoObjectType):
    """Behavior tracking type"""
    id = graphene.ID(required=True)
    user = Field(lambda: UserType)
    session_id = String()
    ip_address = String()
    action = String()
    target_type = String()
    target_id = Int()
    duration = Int()
    metadata = JSONString()
    created_at = DateTime()

    class Meta:
        model = BehaviorTracking
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'session_id': ['exact'],
            'action': ['exact'],
            'target_type': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class ForecastType(DjangoObjectType):
    """Forecast type"""
    id = graphene.ID(required=True)
    product = Field(lambda: ProductType)
    
    # Forecast specifications
    forecast_type = String()
    period = String()
    
    # Forecast values
    predicted_demand = Int()
    actual_demand = Int()
    error_margin = Float()
    algorithm_used = String()
    confidence = Float()
    
    # Computed fields
    accuracy_percentage = Float()
    
    created_at = DateTime()

    class Meta:
        model = Forecast
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'forecast_type': ['exact'],
            'period': ['exact'],
            'algorithm_used': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_accuracy_percentage(self, info):
        """Calculate accuracy percentage if actual demand exists"""
        if self.actual_demand is None or self.predicted_demand == 0:
            return None
        return max(0, 100 - abs((self.actual_demand - self.predicted_demand) / self.predicted_demand * 100))


class CustomerSegmentType(DjangoObjectType):
    """Customer segment type"""
    id = graphene.ID(required=True)
    name = String()
    description = String()
    
    # Segment criteria
    criteria = JSONString()
    
    # Status and priority
    is_active = Boolean()
    priority = Int()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = CustomerSegment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'is_active': ['exact'],
            'priority': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class PricingEngineType(DjangoObjectType):
    """Pricing engine type"""
    id = graphene.ID(required=True)
    
    # Base costs
    raw_material_cost = Float()
    labor_cost = Float()
    international_shipping = Float()
    
    # Overhead and profit
    overhead_percentage = Float()
    profit_margin = Float()
    
    # Dynamic pricing factors
    demand_multiplier = Float()
    competition_factor = Float()
    seasonality_factor = Float()
    inventory_factor = Float()
    
    # AI pricing settings
    ai_pricing_enabled = Boolean()
    ai_model_confidence = Float()
    min_confidence_for_pricing = Float()
    
    # Price ranges and limits
    min_price_margin = Float()
    max_price_increase = Float()
    
    # Regional pricing
    regional_pricing_enabled = Boolean()
    regional_multipliers = JSONString()
    
    # Customer segmentation pricing
    customer_segment_pricing = Boolean()
    segment_multipliers = JSONString()
    
    # Time-based pricing
    time_based_pricing = Boolean()
    hour_multipliers = JSONString()
    day_multipliers = JSONString()
    
    # Update frequency
    auto_update_frequency = Int()
    last_update = DateTime()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = PricingEngine
        interfaces = (relay.Node,)
        fields = '__all__'


class DashboardSettingsType(DjangoObjectType):
    """Dashboard settings type"""
    id = graphene.ID(required=True)
    user = Field(lambda: UserType)
    
    # Layout configuration
    layout = JSONString()
    
    # Widget configuration
    widgets = JSONString()
    
    # Preferences
    preferences = JSONString()
    
    # Data filters
    default_date_range = String()
    default_wilaya = String()
    default_category = Field(lambda: CategoryType)
    
    # Notification settings
    email_notifications = Boolean()
    push_notifications = Boolean()
    notification_frequency = String()
    
    # Privacy settings
    share_analytics = Boolean()
    public_dashboard = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = DashboardSettings
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'default_date_range': ['exact'],
            'notification_frequency': ['exact'],
        }


# Input Types
class BehaviorTrackingInput(graphene.InputObjectType):
    """Input for behavior tracking"""
    action = String(required=True)
    target_type = String()
    target_id = Int()
    session_id = String()
    duration = Int()
    metadata = JSONString()


class ForecastInput(graphene.InputObjectType):
    """Input for forecast creation and updates"""
    product_id = ID()
    forecast_type = String(required=True)
    period = String(required=True)
    predicted_demand = Int()
    actual_demand = Int()
    error_margin = Float()
    algorithm_used = String()
    confidence = Float()


class CustomerSegmentInput(graphene.InputObjectType):
    """Input for customer segment creation and updates"""
    name = String(required=True)
    description = String()
    criteria = JSONString()
    
    # Status and priority
    is_active = Boolean(default_value=True)
    priority = Int(default_value=0)


class PricingEngineInput(graphene.InputObjectType):
    """Input for pricing engine configuration"""
    # Base costs
    raw_material_cost = Float()
    labor_cost = Float()
    international_shipping = Float()
    
    # Overhead and profit
    overhead_percentage = Float()
    profit_margin = Float()
    
    # Dynamic pricing factors
    demand_multiplier = Float()
    competition_factor = Float()
    seasonality_factor = Float()
    inventory_factor = Float()
    
    # AI pricing settings
    ai_pricing_enabled = Boolean()
    ai_model_confidence = Float()
    min_confidence_for_pricing = Float()
    
    # Price ranges and limits
    min_price_margin = Float()
    max_price_increase = Float()
    
    # Regional pricing
    regional_pricing_enabled = Boolean()
    regional_multipliers = JSONString()
    
    # Customer segmentation pricing
    customer_segment_pricing = Boolean()
    segment_multipliers = JSONString()
    
    # Time-based pricing
    time_based_pricing = Boolean()
    hour_multipliers = JSONString()
    day_multipliers = JSONString()
    
    # Update frequency
    auto_update_frequency = Int()


class DashboardSettingsInput(graphene.InputObjectType):
    """Input for dashboard settings"""
    layout = JSONString()
    widgets = JSONString()
    preferences = JSONString()
    
    # Data filters
    default_date_range = String()
    default_wilaya_id = ID()
    default_category_id = ID()
    
    # Notification settings
    email_notifications = Boolean()
    push_notifications = Boolean()
    notification_frequency = String()
    
    # Privacy settings
    share_analytics = Boolean()
    public_dashboard = Boolean()


class TrackUserAction(BaseMutation):
    """Track user behavior action"""
    
    class Arguments:
        input = BehaviorTrackingInput(required=True)

    success = Boolean()
    message = String()
    tracking = Field(BehaviorTrackingType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics_new import (
                BehaviorTracking, Forecast, CustomerSegment, CustomerSegmentUser, PricingEngine
            )
            from django.contrib.auth.models import AnonymousUser
            import uuid
            
            user = info.context.user
            
            # Get client IP address
            ip_address = None
            x_forwarded_for = info.context.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = info.context.META.get('REMOTE_ADDR')
            
            # Generate session ID if not provided and user is anonymous
            session_id = input.get('session_id')
            if not session_id and isinstance(user, AnonymousUser):
                session_id = str(uuid.uuid4())
            
            # Create tracking record
            tracking_data = {
                'user': user if user.is_authenticated else None,
                'session_id': session_id,
                'ip_address': ip_address,
                'action': input['action'],
                'target_type': input.get('target_type'),
                'target_id': input.get('target_id'),
                'duration': input.get('duration', 0),
                'metadata': input.get('metadata', {})
            }
            
            tracking = BehaviorTracking.objects.create(**tracking_data)
            
            return TrackUserAction(
                success=True,
                message="Action tracked successfully",
                tracking=tracking
            )
            
        except Exception as e:
            return TrackUserAction(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Mutations
class CreateForecast(Mutation):
    """Create a new forecast"""
    
    class Arguments:
        input = ForecastInput(required=True)

    success = Boolean()
    message = String()
    forecast = Field(ForecastType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics_new import Forecast
            from api.models.product import Product
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateForecast(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            # Handle product
            product = None
            if 'product_id' in input:
                product = Product.objects.get(id=input['product_id'])
            
            forecast = Forecast.objects.create(
                product=product,
                **{k: v for k, v in input.items() if k != 'product_id'}
            )
            
            return CreateForecast(
                success=True,
                message="Forecast created successfully",
                forecast=forecast
            )
            
        except Exception as e:
            return CreateForecast(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateForecast(Mutation):
    """Update an existing forecast"""
    
    class Arguments:
        id = ID(required=True)
        input = ForecastInput(required=True)

    success = Boolean()
    message = String()
    forecast = Field(ForecastType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            from api.models.analytics_new import Forecast
            from api.models.product import Product
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return UpdateForecast(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            forecast = Forecast.objects.get(id=id)
            
            # Handle product
            if 'product_id' in input:
                forecast.product = Product.objects.get(id=input['product_id'])
            
            # Update fields
            for field, value in input.items():
                if field != 'product_id' and hasattr(forecast, field):
                    setattr(forecast, field, value)
            
            forecast.save()
            
            return UpdateForecast(
                success=True,
                message="Forecast updated successfully",
                forecast=forecast
            )
            
        except Forecast.DoesNotExist:
            return UpdateForecast(
                success=False,
                message="Forecast not found",
                errors=["Forecast not found"]
            )
        except Exception as e:
            return UpdateForecast(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateCustomerSegment(Mutation):
    """Create a new customer segment"""
    
    class Arguments:
        input = CustomerSegmentInput(required=True)

    success = Boolean()
    message = String()
    segment = Field(CustomerSegmentType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics_new import CustomerSegment
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateCustomerSegment(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            segment = CustomerSegment.objects.create(**input)
            
            return CreateCustomerSegment(
                success=True,
                message="Customer segment created successfully",
                segment=segment
            )
            
        except Exception as e:
            return CreateCustomerSegment(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateCustomerSegment(Mutation):
    """Update an existing customer segment"""
    
    class Arguments:
        id = ID(required=True)
        input = CustomerSegmentInput(required=True)

    success = Boolean()
    message = String()
    segment = Field(CustomerSegmentType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            from api.models.analytics_new import CustomerSegment
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return UpdateCustomerSegment(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            segment = CustomerSegment.objects.get(id=id)
            
            # Update fields
            for field, value in input.items():
                if hasattr(segment, field):
                    setattr(segment, field, value)
            
            segment.save()
            
            return UpdateCustomerSegment(
                success=True,
                message="Customer segment updated successfully",
                segment=segment
            )
            
        except CustomerSegment.DoesNotExist:
            return UpdateCustomerSegment(
                success=False,
                message="Customer segment not found",
                errors=["Customer segment not found"]
            )
        except Exception as e:
            return UpdateCustomerSegment(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateDashboardSettings(Mutation):
    """Update dashboard settings"""
    
    class Arguments:
        input = DashboardSettingsInput(required=True)

    success = Boolean()
    message = String()
    dashboard_settings = Field(DashboardSettingsType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics import DashboardSettings
            from api.models.product import Category
            
            user = info.context.user
            
            if not user.is_authenticated:
                return UpdateDashboardSettings(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            dashboard_settings, created = DashboardSettings.objects.get_or_create(user=user)
            
            # Handle category
            if 'default_category_id' in input:
                dashboard_settings.default_category = Category.objects.get(id=input['default_category_id'])
            
            # Update fields
            for field, value in input.items():
                if field != 'default_category_id' and hasattr(dashboard_settings, field):
                    setattr(dashboard_settings, field, value)
            
            dashboard_settings.save()
            
            return UpdateDashboardSettings(
                success=True,
                message="Dashboard settings updated successfully",
                dashboard_settings=dashboard_settings
            )
            
        except Exception as e:
            return UpdateDashboardSettings(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class AnalyticsQuery(ObjectType):
    """Analytics queries"""
    
    # Behavior tracking queries
    behavior_tracking = List(BehaviorTrackingType, user_id=ID(), session_id=String(), action=String())
    
    # Forecast queries
    forecasts = List(ForecastType)
    forecast = Field(ForecastType, id=ID(required=True))
    product_forecasts = List(ForecastType, product_id=ID(required=True))
    
    # Customer segment queries
    customer_segments = List(CustomerSegmentType)
    customer_segment = Field(CustomerSegmentType, id=ID(required=True))
    
    # Pricing engine queries
    pricing_engine = Field(PricingEngineType)
    
    # Dashboard settings queries
    my_dashboard_settings = Field(DashboardSettingsType)
    
    def resolve_behavior_tracking(self, info, user_id=None, session_id=None, action=None):
        """Get behavior tracking records"""
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return []
        
        queryset = BehaviorTracking.objects.all()
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-created_at')[:100]  # Limit to last 100 records
    
    def resolve_forecasts(self, info):
        """Get all forecasts (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            from api.models.analytics_new import Forecast
            return Forecast.objects.all()
        return []
    
    def resolve_forecast(self, info, id):
        """Get forecast by ID"""
        user = info.context.user
        try:
            from api.models.analytics_new import Forecast
            forecast = Forecast.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return forecast
            return None
        except Forecast.DoesNotExist:
            return None
    
    def resolve_product_forecasts(self, info, product_id):
        """Get forecasts for specific product"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            from api.models.analytics_new import Forecast
            return Forecast.objects.filter(product_id=product_id)
        return []
    
    def resolve_customer_segments(self, info):
        """Get all customer segments (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return CustomerSegment.objects.all()
        return []
    
    def resolve_customer_segment(self, info, id):
        """Get customer segment by ID"""
        user = info.context.user
        try:
            segment = CustomerSegment.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return segment
            return None
        except CustomerSegment.DoesNotExist:
            return None
    
    def resolve_pricing_engine(self, info):
        """Get pricing engine configuration (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            try:
                return PricingEngine.objects.first()
            except PricingEngine.DoesNotExist:
                return None
        return None
    
    def resolve_my_dashboard_settings(self, info):
        """Get current user's dashboard settings"""
        user = info.context.user
        if user.is_authenticated:
            try:
                return user.dashboard_settings
            except DashboardSettings.DoesNotExist:
                return None
        return None


# Mutation Class
class AnalyticsMutation(ObjectType):
    """Analytics mutations"""
    
    track_user_action = TrackUserAction.Field()
    create_forecast = CreateForecast.Field()
    update_forecast = UpdateForecast.Field()
    create_customer_segment = CreateCustomerSegment.Field()
    update_customer_segment = UpdateCustomerSegment.Field()
    update_dashboard_settings = UpdateDashboardSettings.Field()
