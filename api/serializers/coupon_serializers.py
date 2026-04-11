"""
Coupon Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.promotion import Coupon, CouponUsage, CouponCampaign


class CouponUsageSerializer(serializers.ModelSerializer):
    """Coupon usage serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = [
            'id', 'coupon', 'user', 'user_name', 'order',
            'order_number', 'discount_amount', 'order_amount_before_discount',
            'ip_address', 'user_agent', 'used_at'
        ]
        read_only_fields = ['id', 'used_at']


class CouponCampaignSerializer(serializers.ModelSerializer):
    """Coupon campaign serializer"""
    is_active_campaign = serializers.SerializerMethodField()
    
    class Meta:
        model = CouponCampaign
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'is_active', 'target_audience', 'budget', 'coupons_count',
            'total_usage', 'total_discount_given', 'conversion_rate',
            'created_by', 'created_at', 'updated_at',
            'is_active_campaign'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_active_campaign(self, obj):
        """Check if campaign is currently active"""
        return obj.is_active_campaign


class CouponSerializer(serializers.ModelSerializer):
    """Coupon serializer"""
    is_valid = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'usage_limit', 'usage_limit_per_user',
            'used_count', 'min_amount', 'max_discount',
            'applicable_products', 'excluded_products',
            'applicable_categories', 'excluded_categories',
            'applicable_wilayas', 'applicable_user_segments',
            'first_time_customers_only', 'valid_from', 'valid_to',
            'is_active', 'auto_apply', 'stackable', 'buy_quantity',
            'get_quantity', 'get_product_id', 'tiers',
            'times_used', 'total_discount_given', 'average_order_value',
            'created_by', 'campaign', 'created_at', 'updated_at',
            'is_valid', 'days_until_expiry', 'usage_stats'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_valid(self, obj):
        """Check if coupon is currently valid"""
        return obj.is_valid
    
    def get_days_until_expiry(self, obj):
        """Calculate days until coupon expires"""
        return obj.days_until_expiry
    
    def get_usage_stats(self, obj):
        """Get usage statistics"""
        return {
            'total_used': obj.used_count,
            'remaining': obj.usage_limit - obj.used_count if obj.usage_limit else None,
            'usage_percentage': (obj.used_count / obj.usage_limit * 100) if obj.usage_limit else 0
        }


class CouponCreateSerializer(serializers.ModelSerializer):
    """Coupon creation serializer"""
    class Meta:
        model = Coupon
        fields = [
            'code', 'name', 'description', 'discount_type',
            'discount_value', 'usage_limit', 'usage_limit_per_user',
            'min_amount', 'max_discount', 'applicable_products',
            'excluded_products', 'applicable_categories',
            'excluded_categories', 'applicable_wilayas',
            'applicable_user_segments', 'first_time_customers_only',
            'valid_from', 'valid_to', 'is_active', 'auto_apply',
            'stackable', 'buy_quantity', 'get_quantity',
            'get_product_id', 'tiers'
        ]
    
    def validate_code(self, value):
        """Validate coupon code uniqueness"""
        if Coupon.objects.filter(code=value.upper()).exists():
            raise serializers.ValidationError("Coupon code already exists")
        return value.upper()
    
    def validate_discount_value(self, value):
        """Validate discount value"""
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0")
        return value
    
    def validate(self, data):
        """Validate coupon dates and logic"""
        if data.get('valid_from') and data.get('valid_to'):
            if data['valid_from'] >= data['valid_to']:
                raise serializers.ValidationError(
                    "Valid from date must be before valid to date"
                )
        
        if data.get('discount_type') == 'percentage' and data.get('discount_value', 0) > 100:
            raise serializers.ValidationError(
                "Percentage discount cannot exceed 100%"
            )
        
        return data
    
    def create(self, validated_data):
        """Create coupon"""
        validated_data['code'] = validated_data['code'].upper()
        return Coupon.objects.create(**validated_data)


class CouponUpdateSerializer(serializers.ModelSerializer):
    """Coupon update serializer"""
    class Meta:
        model = Coupon
        fields = [
            'name', 'description', 'discount_type', 'discount_value',
            'usage_limit', 'usage_limit_per_user', 'min_amount',
            'max_discount', 'applicable_products', 'excluded_products',
            'applicable_categories', 'excluded_categories',
            'applicable_wilayas', 'applicable_user_segments',
            'first_time_customers_only', 'valid_from', 'valid_to',
            'is_active', 'auto_apply', 'stackable', 'buy_quantity',
            'get_quantity', 'get_product_id', 'tiers'
        ]
    
    def validate_discount_value(self, value):
        """Validate discount value"""
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0")
        return value
    
    def validate(self, data):
        """Validate coupon dates and logic"""
        if data.get('valid_from') and data.get('valid_to'):
            if data['valid_from'] >= data['valid_to']:
                raise serializers.ValidationError(
                    "Valid from date must be before valid to date"
                )
        
        if data.get('discount_type') == 'percentage' and data.get('discount_value', 0) > 100:
            raise serializers.ValidationError(
                "Percentage discount cannot exceed 100%"
            )
        
        return data
    
    def update(self, instance, validated_data):
        """Update coupon"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CouponCampaignCreateSerializer(serializers.ModelSerializer):
    """Coupon campaign creation serializer"""
    class Meta:
        model = CouponCampaign
        fields = [
            'name', 'description', 'start_date', 'end_date',
            'is_active', 'target_audience', 'budget'
        ]
    
    def validate(self, data):
        """Validate campaign dates"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "Start date must be before end date"
                )
        return data
    
    def create(self, validated_data):
        """Create coupon campaign"""
        return CouponCampaign.objects.create(**validated_data)


class CouponApplySerializer(serializers.Serializer):
    """Coupon application serializer"""
    code = serializers.CharField(required=True)
    order_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    user_id = serializers.IntegerField(required=False)
    
    def validate_code(self, value):
        """Validate coupon code"""
        try:
            coupon = Coupon.objects.get(
                code=value.upper(),
                is_active=True
            )
            if not coupon.is_valid:
                raise serializers.ValidationError("Coupon is not valid")
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Coupon not found")
    
    def validate(self, data):
        """Validate coupon against order amount and user"""
        coupon = data['code']
        order_amount = data.get('order_amount', 0)
        user_id = data.get('user_id')
        
        # Check minimum amount
        if coupon.min_amount and order_amount < coupon.min_amount:
            raise serializers.ValidationError(
                f"Minimum order amount of {coupon.min_amount} required"
            )
        
        # Check user usage limit
        if coupon.usage_limit_per_user and user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user_usage = CouponUsage.objects.filter(
                coupon=coupon,
                user_id=user_id
            ).count()
            
            if user_usage >= coupon.usage_limit_per_user:
                raise serializers.ValidationError(
                    "Coupon usage limit exceeded for this user"
                )
        
        return data
    
    def save(self):
        """Apply coupon and create usage record"""
        coupon = self.validated_data['code']
        order_amount = self.validated_data.get('order_amount', 0)
        user_id = self.validated_data.get('user_id')
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(order_amount)
        
        # Create usage record if user is provided
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user = User.objects.get(id=user_id)
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                discount_amount=discount_amount,
                order_amount_before_discount=order_amount
            )
        
        return {
            'coupon': coupon,
            'discount_amount': discount_amount,
            'order_amount': order_amount,
            'final_amount': order_amount - discount_amount
        }
