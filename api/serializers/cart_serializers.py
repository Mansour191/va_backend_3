"""
Cart Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from core.models import CartItem, Product, Material, Coupon


class CouponSerializer(serializers.ModelSerializer):
    """Coupon serializer"""
    is_valid = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
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
            'is_valid', 'days_until_expiry'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_valid(self, obj):
        """Check if coupon is currently valid"""
        return obj.is_valid
    
    def get_days_until_expiry(self, obj):
        """Calculate days until coupon expires"""
        return obj.days_until_expiry


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    material_name = serializers.CharField(source='material.name_ar', read_only=True)
    product_image = serializers.CharField(source='product.main_image', read_only=True)
    subtotal = serializers.SerializerMethodField()
    total_with_discount = serializers.SerializerMethodField()
    final_total = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    max_quantity = serializers.SerializerMethodField()
    coupon_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'user', 'session_id', 'product', 'product_name',
            'material', 'material_name', 'quantity', 'options',
            'width', 'height', 'dimension_unit', 'unit_price',
            'material_price', 'discount_amount', 'delivery_type',
            'wilaya', 'shipping_cost', 'applied_coupon',
            'coupon_discount', 'created_at', 'updated_at',
            'product_image', 'subtotal', 'total_with_discount',
            'final_total', 'is_available', 'max_quantity',
            'coupon_info'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subtotal(self, obj):
        """Calculate subtotal for this item"""
        return (obj.unit_price + obj.material_price) * obj.quantity
    
    def get_total_with_discount(self, obj):
        """Calculate total after discount"""
        subtotal = self.get_subtotal(obj)
        return max(0, subtotal - obj.discount_amount - obj.coupon_discount)
    
    def get_final_total(self, obj):
        """Calculate final total including shipping"""
        return self.get_total_with_discount(obj) + obj.shipping_cost
    
    def get_is_available(self, obj):
        """Check if product is available"""
        return obj.product.is_active and obj.product.stock >= obj.quantity
    
    def get_max_quantity(self, obj):
        """Get maximum quantity available"""
        return obj.product.stock
    
    def get_coupon_info(self, obj):
        """Get coupon information"""
        if obj.applied_coupon:
            return {
                'code': obj.applied_coupon.code,
                'discount': obj.coupon_discount,
                'type': obj.applied_coupon.discount_type
            }
        return None


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Cart item creation serializer"""
    coupon_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CartItem
        fields = [
            'product', 'material', 'quantity', 'options',
            'width', 'height', 'dimension_unit', 'delivery_type',
            'wilaya', 'coupon_code'
        ]
    
    def create(self, validated_data):
        """Create cart item"""
        coupon_code = validated_data.pop('coupon_code', None)
        
        # Create cart item
        cart_item = CartItem.objects.create(**validated_data)
        
        # Apply coupon if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code.upper(),
                    is_active=True
                )
                if coupon.is_valid:
                    cart_item.applied_coupon = coupon
                    cart_item.coupon_discount = coupon.calculate_discount(
                        cart_item.subtotal
                    )
                    cart_item.save()
            except Coupon.DoesNotExist:
                pass
        
        return cart_item


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Cart item update serializer"""
    class Meta:
        model = CartItem
        fields = [
            'quantity', 'options', 'width', 'height',
            'delivery_type', 'wilaya'
        ]
    
    def update(self, instance, validated_data):
        """Update cart item"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CouponValidateSerializer(serializers.Serializer):
    """Coupon validation serializer"""
    code = serializers.CharField(required=True)
    order_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    
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
        """Validate coupon against order amount"""
        coupon = data['code']
        order_amount = data.get('order_amount', 0)
        
        if 'min_amount' in coupon and order_amount < coupon.min_amount:
            raise serializers.ValidationError(
                f"Minimum order amount of {coupon.min_amount} required"
            )
        
        return data


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Simple product serializer for cart items"""
    
    class Meta:
        model = Product
        fields = ['id', 'name_ar', 'name_en', 'base_price', 'stock', 'is_active']


class MaterialSimpleSerializer(serializers.ModelSerializer):
    """Simple material serializer for cart items"""
    
    class Meta:
        model = Material
        fields = ['id', 'name_ar', 'name_en', 'price_per_m2']


class CartSummarySerializer(serializers.Serializer):
    """Serializer for cart summary"""
    
    total_items = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
