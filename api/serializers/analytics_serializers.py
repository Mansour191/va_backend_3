"""
Analytics Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.analytics_new import (
    BehaviorTracking, Forecast, CustomerSegment, CustomerSegmentUser, PricingEngine
)


class ForecastSerializer(serializers.ModelSerializer):
    """Forecast serializer"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    category_name = serializers.CharField(source='category.name_ar', read_only=True)
    accuracy_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Forecast
        fields = [
            'id', 'product', 'product_name', 'category',
            'category_name', 'forecast_type', 'period', 'model_used',
            'start_date', 'end_date', 'forecast_date',
            'predicted_value', 'confidence_interval_lower',
            'confidence_interval_upper', 'confidence',
            'actual_value', 'mae', 'mape', 'model_parameters',
            'training_data_points', 'seasonal_adjustment',
            'created_at', 'updated_at', 'accuracy_percentage'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_accuracy_percentage(self, obj):
        """Calculate accuracy percentage if actual value exists"""
        return obj.accuracy_percentage


class CustomerSegmentSerializer(serializers.ModelSerializer):
    """Customer segment serializer"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerSegment
        fields = [
            'id', 'name', 'description', 'criteria', 'is_active', 'priority',
            'created_at', 'updated_at', 'user_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        """Get actual user count in segment"""
        # This would implement the actual filtering logic
        # based on the criteria JSON
        return CustomerSegmentUser.objects.filter(customersegment=obj).count()


class PricingEngineSerializer(serializers.ModelSerializer):
    """Pricing engine serializer"""
    class Meta:
        model = PricingEngine
        fields = [
            'id', 'raw_material_cost', 'labor_cost',
            'international_shipping', 'overhead_percentage',
            'profit_margin', 'demand_multiplier', 'competition_factor',
            'seasonality_factor', 'inventory_factor',
            'ai_pricing_enabled', 'ai_model_confidence',
            'min_confidence_for_pricing', 'min_price_margin',
            'max_price_increase', 'regional_pricing_enabled',
            'regional_multipliers', 'customer_segment_pricing',
            'segment_multipliers', 'time_based_pricing',
            'hour_multipliers', 'day_multipliers',
            'auto_update_frequency', 'last_update', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSettingsSerializer(serializers.ModelSerializer):
    """Dashboard settings serializer"""
    default_category_name = serializers.CharField(
        source='default_category.name_ar', read_only=True, allow_null=True
    )
    
    class Meta:
        model = DashboardSettings
        fields = [
            'id', 'user', 'layout', 'widgets', 'preferences',
            'default_date_range', 'default_wilaya',
            'default_category', 'default_category_name',
            'email_notifications', 'push_notifications',
            'notification_frequency', 'share_analytics',
            'public_dashboard', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ForecastCreateSerializer(serializers.ModelSerializer):
    """Forecast creation serializer"""
    class Meta:
        model = Forecast
        fields = [
            'product', 'category', 'forecast_type', 'period',
            'model_used', 'start_date', 'end_date',
            'forecast_date', 'predicted_value',
            'confidence_interval_lower', 'confidence_interval_upper',
            'confidence', 'model_parameters', 'training_data_points',
            'seasonal_adjustment'
        ]
    
    def validate(self, data):
        """Validate forecast data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date"
            )
        
        return data
    
    def create(self, validated_data):
        """Create forecast"""
        return Forecast.objects.create(**validated_data)


class CustomerSegmentCreateSerializer(serializers.ModelSerializer):
    """Customer segment creation serializer"""
    class Meta:
        model = CustomerSegment
        fields = [
            'name', 'description', 'criteria', 'is_active', 'priority'
        ]
    
    def create(self, validated_data):
        """Create customer segment"""
        return CustomerSegment.objects.create(**validated_data)


class PricingEngineUpdateSerializer(serializers.ModelSerializer):
    """Pricing engine update serializer"""
    class Meta:
        model = PricingEngine
        fields = [
            'raw_material_cost', 'labor_cost', 'international_shipping',
            'overhead_percentage', 'profit_margin', 'demand_multiplier',
            'competition_factor', 'seasonality_factor',
            'inventory_factor', 'ai_pricing_enabled',
            'ai_model_confidence', 'min_confidence_for_pricing',
            'min_price_margin', 'max_price_increase',
            'regional_pricing_enabled', 'regional_multipliers',
            'customer_segment_pricing', 'segment_multipliers',
            'time_based_pricing', 'hour_multipliers',
            'day_multipliers', 'auto_update_frequency'
        ]
    
    def validate(self, data):
        """Validate pricing engine data"""
        if data.get('min_confidence_for_pricing', 0) > 1:
            raise serializers.ValidationError(
                "Minimum confidence for pricing cannot exceed 1.0"
            )
        
        if data.get('max_price_increase', 0) < 0:
            raise serializers.ValidationError(
                "Maximum price increase cannot be negative"
            )
        
        return data
    
    def update(self, instance, validated_data):
        """Update pricing engine"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DashboardSettingsUpdateSerializer(serializers.ModelSerializer):
    """Dashboard settings update serializer"""
    class Meta:
        model = DashboardSettings
        fields = [
            'layout', 'widgets', 'preferences',
            'default_date_range', 'default_wilaya',
            'default_category', 'email_notifications',
            'push_notifications', 'notification_frequency',
            'share_analytics', 'public_dashboard'
        ]
    
    def update(self, instance, validated_data):
        """Update dashboard settings"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ForecastAccuracyUpdateSerializer(serializers.Serializer):
    """Forecast accuracy update serializer"""
    forecast_id = serializers.IntegerField(required=True)
    actual_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=True
    )
    
    def validate_forecast_id(self, value):
        """Validate forecast exists"""
        if not Forecast.objects.filter(id=value).exists():
            raise serializers.ValidationError("Forecast not found")
        return value
    
    def save(self):
        """Update forecast accuracy"""
        forecast_id = self.validated_data['forecast_id']
        actual_value = self.validated_data['actual_value']
        
        try:
            forecast = Forecast.objects.get(id=forecast_id)
            forecast.calculate_accuracy(actual_value)
            return {
                'status': 'success',
                'message': 'Forecast accuracy updated',
                'accuracy_percentage': forecast.accuracy_percentage
            }
        
        except Forecast.DoesNotExist:
            return {'status': 'error', 'message': 'Forecast not found'}


class AnalyticsSummarySerializer(serializers.Serializer):
    """Analytics summary serializer"""
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    segment_type = serializers.CharField(required=False)
    
    def validate(self, data):
        """Validate date range"""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "date_from must be before date_to"
            )
        
        return data
    
    def save(self):
        """Generate analytics summary"""
        filters = {}
        
        if self.validated_data.get('date_from'):
            filters['created_at__gte'] = self.validated_data['date_from']
        
        if self.validated_data.get('date_to'):
            filters['created_at__lte'] = self.validated_data['date_to']
        
        if self.validated_data.get('segment_type'):
            filters['segment_type'] = self.validated_data['segment_type']
        
        segments = CustomerSegment.objects.filter(**filters)
        forecasts = Forecast.objects.filter(**filters)
        
        return {
            'total_segments': segments.count(),
            'active_segments': segments.filter(is_active=True).count(),
            'total_forecasts': forecasts.count(),
            'accurate_forecasts': forecasts.filter(
                actual_value__isnull=False
            ).count(),
            'average_accuracy': self.calculate_average_accuracy(forecasts),
            'segments_by_type': segments.values('segment_type').annotate(
                count=models.Count('segment_type')
            ),
            'forecasts_by_type': forecasts.values('forecast_type').annotate(
                count=models.Count('forecast_type')
            )
        }
    
    def calculate_average_accuracy(self, forecasts):
        """Calculate average forecast accuracy"""
        accurate_forecasts = forecasts.filter(actual_value__isnull=False)
        
        if not accurate_forecasts.exists():
            return None
        
        total_accuracy = 0
        for forecast in accurate_forecasts:
            accuracy = forecast.accuracy_percentage
            if accuracy is not None:
                total_accuracy += accuracy
        
        return total_accuracy / accurate_forecasts.count()
