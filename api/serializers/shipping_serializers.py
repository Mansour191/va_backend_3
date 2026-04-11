"""
Shipping Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.shipping import Shipping, ShippingMethod, ShippingPrice


class ShippingPriceSerializer(serializers.ModelSerializer):
    """Shipping price serializer"""
    wilaya_name = serializers.CharField(source='wilaya.name_ar', read_only=True)
    method_name = serializers.CharField(source='shipping_method.name', read_only=True)
    
    class Meta:
        model = ShippingPrice
        fields = [
            'id', 'wilaya', 'shipping_method', 'wilaya_name', 'method_name',
            'home_delivery_price', 'stop_desk_price', 'express_price',
            'pickup_price', 'free_shipping_minimum', 'weight_surcharge',
            'volume_surcharge', 'cod_available', 'cod_fee',
            'insurance_available', 'insurance_rate', 'tracking_available',
            'max_weight', 'max_value', 'is_active', 'valid_from',
            'valid_to', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Shipping method serializer"""
    prices = ShippingPriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = ShippingMethod
        fields = [
            'id', 'name', 'provider', 'service_type',
            'expected_delivery_time', 'delivery_days', 'cutoff_time',
            'logo', 'description', 'contact_phone', 'contact_email',
            'is_active', 'tracking_available', 'insurance_available',
            'cod_available', 'coverage_wilayas', 'max_weight',
            'max_dimensions', 'tracking_url_template', 'api_endpoint',
            'api_key', 'created_at', 'updated_at', 'prices'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShippingSerializer(serializers.ModelSerializer):
    """Shipping serializer"""
    available_shipping_methods = serializers.SerializerMethodField()
    base_city_name = serializers.CharField(source='base_city.name', read_only=True)
    
    class Meta:
        model = Shipping
        fields = [
            'id', 'wilaya_id', 'wilaya_code', 'name_ar', 'name_en',
            'region', 'is_active', 'is_metropolitan', 'pickup_latitude',
            'pickup_longitude', 'radius_km', 'maps_url',
            'home_delivery_available', 'stop_desk_available',
            'express_available', 'pickup_point_available',
            'base_city', 'base_city_name', 'created_at', 'updated_at',
            'available_shipping_methods'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_available_shipping_methods(self, obj):
        """Get available shipping methods for this wilaya"""
        methods = obj.get_available_shipping_methods()
        return ShippingMethodSerializer(methods, many=True).data


class ShippingCreateSerializer(serializers.ModelSerializer):
    """Shipping creation serializer"""
    class Meta:
        model = Shipping
        fields = [
            'wilaya_id', 'wilaya_code', 'name_ar', 'name_en',
            'region', 'is_active', 'is_metropolitan',
            'pickup_latitude', 'pickup_longitude', 'radius_km',
            'maps_url', 'home_delivery_available',
            'stop_desk_available', 'express_available',
            'pickup_point_available', 'base_city'
        ]
    
    def create(self, validated_data):
        """Create shipping"""
        return Shipping.objects.create(**validated_data)


class ShippingMethodCreateSerializer(serializers.ModelSerializer):
    """Shipping method creation serializer"""
    class Meta:
        model = ShippingMethod
        fields = [
            'name', 'provider', 'service_type', 'expected_delivery_time',
            'delivery_days', 'cutoff_time', 'logo', 'description',
            'contact_phone', 'contact_email', 'is_active',
            'tracking_available', 'insurance_available', 'cod_available',
            'coverage_wilayas', 'max_weight', 'max_dimensions',
            'tracking_url_template', 'api_endpoint', 'api_key'
        ]
    
    def create(self, validated_data):
        """Create shipping method"""
        return ShippingMethod.objects.create(**validated_data)


class ShippingPriceCreateSerializer(serializers.ModelSerializer):
    """Shipping price creation serializer"""
    class Meta:
        model = ShippingPrice
        fields = [
            'wilaya', 'shipping_method', 'home_delivery_price',
            'stop_desk_price', 'express_price', 'pickup_price',
            'free_shipping_minimum', 'weight_surcharge', 'volume_surcharge',
            'cod_available', 'cod_fee', 'insurance_available',
            'insurance_rate', 'tracking_available', 'max_weight',
            'max_value', 'is_active', 'valid_from', 'valid_to'
        ]
    
    def create(self, validated_data):
        """Create shipping price"""
        return ShippingPrice.objects.create(**validated_data)


class ShippingWithPricesSerializer(serializers.ModelSerializer):
    """Enhanced Shipping serializer with available methods and prices"""
    
    available_methods = serializers.SerializerMethodField()
    best_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipping
        fields = '__all__'
    
    def get_available_methods(self, obj):
        """Get all available shipping methods for this wilaya"""
        prices = ShippingPrice.objects.filter(
            wilaya=obj,
            is_active=True,
            shipping_method__is_active=True
        ).select_related('shipping_method')
        
        return ShippingPriceSerializer(prices, many=True).data
    
    def get_best_prices(self, obj):
        """Get best prices per service type"""
        prices = ShippingPrice.objects.filter(
            wilaya=obj,
            is_active=True,
            shipping_method__is_active=True
        ).select_related('shipping_method')
        
        result = {}
        
        # Group by service type and find best price
        for price in prices:
            service_type = price.shipping_method.service_type
            
            if service_type not in result:
                result[service_type] = {
                    'price': float(price.home_delivery_price),
                    'method': ShippingMethodSerializer(price.shipping_method).data
                }
            else:
                current_price = result[service_type]['price']
                if price.home_delivery_price < current_price:
                    result[service_type] = {
                        'price': float(price.home_delivery_price),
                        'method': ShippingMethodSerializer(price.shipping_method).data
                    }
        
        return result


class ShippingCalculationSerializer(serializers.Serializer):
    """Serializer for shipping calculation requests"""
    
    wilaya_id = serializers.CharField()
    delivery_type = serializers.ChoiceField(
        choices=['home', 'stop_desk', 'express'],
        default='home'
    )
    order_weight = serializers.DecimalField(required=False, allow_null=True)
    order_volume = serializers.DecimalField(required=False, allow_null=True)
    order_total = serializers.DecimalField(required=False, allow_null=True)


class BulkUpdateShippingSerializer(serializers.Serializer):
    """Serializer for bulk shipping updates"""
    
    wilaya_ids = serializers.ListField(
        child=serializers.CharField()
    )
    updates = serializers.DictField()
    
    home_delivery_price = serializers.DecimalField(required=False, allow_null=True)
    stop_desk_price = serializers.DecimalField(required=False, allow_null=True)
    express_delivery_price = serializers.DecimalField(required=False, allow_null=True)
    free_shipping_minimum = serializers.DecimalField(required=False, allow_null=True)
    delivery_time_days = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
