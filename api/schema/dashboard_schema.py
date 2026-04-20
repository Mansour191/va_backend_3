"""
Dashboard Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from api.models.dashboard import DashboardSettings


class DashboardSettingsType(DjangoObjectType):
    """Dashboard settings type"""
    id = graphene.ID(required=True)
    user = Field('api.schema.user_schema.UserType')
    layout_config = JSONString()
    widget_preferences = JSONString()
    theme_settings = JSONString()
    notification_settings = JSONString()
    is_active = Boolean()
    
    # Computed fields
    widget_count = Int()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = DashboardSettings
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'is_active': ['exact'],
        }

    def resolve_widget_count(self, info):
        """Count number of widgets"""
        if self.layout_config and isinstance(self.layout_config, dict):
            return len(self.layout_config.get('widgets', []))
        return 0


# Dashboard Statistics Types
class DashboardStatsType(graphene.ObjectType):
    """Dashboard statistics type"""
    total_sales = Float()
    total_orders = Int()
    total_customers = Int()
    total_products = Int()
    revenue_growth = Float()
    order_growth = Float()
    customer_growth = Float()
    product_growth = Float()
    
    # Period comparisons
    today_sales = Float()
    yesterday_sales = Float()
    this_month_sales = Float()
    last_month_sales = Float()
    this_year_sales = Float()
    last_year_sales = Float()


class TopProductType(graphene.ObjectType):
    """Top product type"""
    id = ID()
    name_ar = String()
    name_en = String()
    total_sales = Float()
    quantity_sold = Int()
    revenue = Float()


class RecentOrderType(graphene.ObjectType):
    """Recent order type"""
    id = ID()
    order_number = String()
    customer_name = String()
    total_amount = Float()
    status = String()
    created_at = DateTime()


# Input Types
class DashboardSettingsInput(graphene.InputObjectType):
    """Input for dashboard settings creation and updates"""
    layout_config = JSONString()
    widget_preferences = JSONString()
    theme_settings = JSONString()
    notification_settings = JSONString()
    is_active = Boolean()


# Mutations
class CreateDashboardSettings(Mutation):
    """Create dashboard settings for user"""
    
    class Arguments:
        input = DashboardSettingsInput(required=True)

    success = Boolean()
    message = String()
    settings = Field(DashboardSettingsType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            user = info.context.user
            
            if not user.is_authenticated:
                return CreateDashboardSettings(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            # Check if settings already exist
            existing_settings = DashboardSettings.objects.filter(user=user).first()
            if existing_settings:
                return CreateDashboardSettings(
                    success=False,
                    message="Dashboard settings already exist",
                    errors=["Dashboard settings already exist"]
                )
            
            settings = DashboardSettings.objects.create(user=user, **input)
            
            return CreateDashboardSettings(
                success=True,
                message="Dashboard settings created successfully",
                settings=settings
            )
            
        except Exception as e:
            return CreateDashboardSettings(
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
    settings = Field(DashboardSettingsType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            user = info.context.user
            
            if not user.is_authenticated:
                return UpdateDashboardSettings(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            settings = DashboardSettings.objects.filter(user=user).first()
            if not settings:
                # Create if doesn't exist
                settings = DashboardSettings.objects.create(user=user, **input)
            else:
                # Update existing
                for field, value in input.items():
                    if hasattr(settings, field):
                        setattr(settings, field, value)
                settings.save()
            
            return UpdateDashboardSettings(
                success=True,
                message="Dashboard settings updated successfully",
                settings=settings
            )
            
        except Exception as e:
            return UpdateDashboardSettings(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class DashboardQuery(ObjectType):
    """Dashboard queries"""
    
    dashboard_settings = Field(DashboardSettingsType)
    dashboard_stats = Field(DashboardStatsType)
    top_products = List(TopProductType, limit=Int(default_value=10))
    recent_orders = List(RecentOrderType, limit=Int(default_value=10))
    sales_overview = JSONString(period=String(default_value="month"))
    
    def resolve_dashboard_settings(self, info):
        """Get dashboard settings for current user"""
        user = info.context.user
        if user.is_authenticated:
            return DashboardSettings.objects.filter(user=user).first()
        return None
    
    def resolve_dashboard_stats(self, info):
        """Get dashboard statistics"""
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return None
        
        # Calculate statistics
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        this_month = today.replace(day=1)
        last_month = this_month - timedelta(days=1)
        this_year = today.replace(month=1, day=1)
        last_year = this_year.replace(year=this_year.year - 1)
        
        # Get order statistics
        from api.models.order import Order
        orders = Order.objects.all()
        
        today_sales = orders.filter(created_at__date=today).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        yesterday_sales = orders.filter(created_at__date=yesterday).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        this_month_sales = orders.filter(created_at__gte=this_month).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        last_month_sales = orders.filter(
            created_at__gte=last_month.replace(day=1),
            created_at__lt=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        this_year_sales = orders.filter(created_at__gte=this_year).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        last_year_sales = orders.filter(
            created_at__gte=last_year,
            created_at__lt=this_year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = orders.count()
        
        # Get customer statistics
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_customers = User.objects.count()
        
        # Get product statistics
        from api.models.product import Product
        total_products = Product.objects.count()
        
        # Calculate growth rates
        revenue_growth = ((this_month_sales - last_month_sales) / last_month_sales * 100) if last_month_sales > 0 else 0
        order_growth = ((orders.filter(created_at__gte=this_month).count() - 
                        orders.filter(created_at__gte=last_month.replace(day=1), created_at__lt=this_month).count()) /
                       orders.filter(created_at__gte=last_month.replace(day=1), created_at__lt=this_month).count() * 100) if orders.filter(created_at__gte=last_month.replace(day=1), created_at__lt=this_month).count() > 0 else 0
        
        return DashboardStatsType(
            total_sales=total_sales,
            total_orders=total_orders,
            total_customers=total_customers,
            total_products=total_products,
            revenue_growth=revenue_growth,
            order_growth=order_growth,
            customer_growth=0,  # Calculate similarly if needed
            product_growth=0,  # Calculate similarly if needed
            today_sales=today_sales,
            yesterday_sales=yesterday_sales,
            this_month_sales=this_month_sales,
            last_month_sales=last_month_sales,
            this_year_sales=this_year_sales,
            last_year_sales=last_year_sales
        )
    
    def resolve_top_products(self, info, limit=10):
        """Get top selling products"""
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return []
        
        from api.models.order import OrderItem
        from api.models.product import Product
        
        top_products = OrderItem.objects.values('product_id').annotate(
            total_sales=Sum('quantity'),
            revenue=Sum('price')
        ).order_by('-total_sales')[:limit]
        
        result = []
        for item in top_products:
            try:
                product = Product.objects.get(id=item['product_id'])
                result.append(TopProductType(
                    id=product.id,
                    name_ar=product.name_ar,
                    name_en=product.name_en,
                    total_sales=item['total_sales'],
                    quantity_sold=item['total_sales'],
                    revenue=item['revenue']
                ))
            except Product.DoesNotExist:
                continue
        
        return result
    
    def resolve_recent_orders(self, info, limit=10):
        """Get recent orders"""
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return []
        
        from api.models.order import Order
        
        orders = Order.objects.all().order_by('-created_at')[:limit]
        
        return [
            RecentOrderType(
                id=order.id,
                order_number=order.order_number,
                customer_name=order.customer_name or f"Customer {order.customer_id}",
                total_amount=order.total_amount,
                status=order.status,
                created_at=order.created_at
            )
            for order in orders
        ]
    
    def resolve_sales_overview(self, info, period="month"):
        """Get sales overview data"""
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return {}
        
        from api.models.order import Order
        
        # Generate time series data based on period
        now = timezone.now()
        
        if period == "day":
            # Last 24 hours
            start_time = now - timedelta(hours=24)
            orders = Order.objects.filter(created_at__gte=start_time)
            # Group by hour
            data = {}
            for order in orders:
                hour = order.created_at.strftime('%H:00')
                data[hour] = data.get(hour, 0) + float(order.total_amount)
            return data
        
        elif period == "week":
            # Last 7 days
            start_time = now - timedelta(days=7)
            orders = Order.objects.filter(created_at__gte=start_time)
            # Group by day
            data = {}
            for order in orders:
                day = order.created_at.strftime('%Y-%m-%d')
                data[day] = data.get(day, 0) + float(order.total_amount)
            return data
        
        elif period == "month":
            # Last 30 days
            start_time = now - timedelta(days=30)
            orders = Order.objects.filter(created_at__gte=start_time)
            # Group by day
            data = {}
            for order in orders:
                day = order.created_at.strftime('%Y-%m-%d')
                data[day] = data.get(day, 0) + float(order.total_amount)
            return data
        
        elif period == "year":
            # Last 12 months
            start_time = now - timedelta(days=365)
            orders = Order.objects.filter(created_at__gte=start_time)
            # Group by month
            data = {}
            for order in orders:
                month = order.created_at.strftime('%Y-%m')
                data[month] = data.get(month, 0) + float(order.total_amount)
            return data
        
        return {}


# Mutation Class
class DashboardMutation(ObjectType):
    """Dashboard mutations"""
    
    create_dashboard_settings = CreateDashboardSettings.Field()
    update_dashboard_settings = UpdateDashboardSettings.Field()
