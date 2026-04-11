"""
Order Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from decimal import Decimal
from api.models.order import Order, OrderItem, OrderTimeline, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer with price locking"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    material_name = serializers.CharField(source='material.name_ar', read_only=True)
    subtotal = serializers.SerializerMethodField()
    original_product_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name', 'material',
            'material_name', 'width', 'height', 'dimension_unit',
            'marble_texture', 'custom_design', 'quantity', 'price',
            'original_product_price', 'created_at', 'updated_at', 'subtotal'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subtotal(self, obj):
        """Calculate subtotal for this item"""
        return obj.price * obj.quantity
    
    def get_original_product_price(self, obj):
        """Get the original product price at time of order"""
        if hasattr(obj, '_original_product_price'):
            return obj._original_product_price
        return obj.product.base_price if obj.product else None
    
    def validate(self, data):
        """Validate order item data including dimensions"""
        # Validate dimensions are positive
        width = data.get('width')
        height = data.get('height')
        
        if width and width <= 0:
            raise serializers.ValidationError("Width must be greater than 0")
        
        if height and height <= 0:
            raise serializers.ValidationError("Height must be greater than 0")
        
        # Calculate area for pricing validation
        if width and height:
            area = width * height  # in cm²
            
            # Validate price is reasonable for the area
            price = data.get('price')
            if price and price <= 0:
                raise serializers.ValidationError("Price must be greater than 0")
            
            # Optional: Check if price matches expected calculation
            product = data.get('product')
            if product and hasattr(product, 'base_price'):
                # Base price per unit area validation
                min_price = Decimal('0.01') * area  # Minimum 0.01 per cm²
                if price < min_price:
                    raise serializers.ValidationError(
                        f"Price seems too low for the specified dimensions. "
                        f"Minimum expected price: {min_price:.2f}"
                    )
        
        return data
    
    def create(self, validated_data):
        """Create order item with locked price"""
        product = validated_data.get('product')
        
        # Store original product price for reference
        if product:
            validated_data['_original_product_price'] = product.base_price
            
            # If no price provided, calculate from product base price
            if 'price' not in validated_data:
                width = validated_data.get('width', 1)
                height = validated_data.get('height', 1)
                area = width * height / 10000  # Convert cm² to m²
                
                # Calculate price based on area and material
                material = validated_data.get('material')
                if material and hasattr(material, 'price_per_m2'):
                    validated_data['price'] = product.base_price + (material.price_per_m2 * area)
                else:
                    validated_data['price'] = product.base_price
        
        return super().create(validated_data)


class OrderTimelineSerializer(serializers.ModelSerializer):
    """Order timeline serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OrderTimeline
        fields = [
            'id', 'order', 'status', 'note', 'user',
            'user_name', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer with enhanced validation"""
    is_successful = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    method_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'method', 'method_display', 'status', 'status_display',
            'transaction_id', 'gateway_response',
            'created_at', 'updated_at', 'is_successful'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_successful(self, obj):
        """Check if payment was successful"""
        return obj.status == 'completed'
    
    def get_status_display(self, obj):
        """Get human readable status"""
        status_labels = {
            'pending': 'في الانتظار',
            'processing': 'قيد المعالجة',
            'completed': 'مكتمل',
            'failed': 'فشل',
            'cancelled': 'ملغي',
            'refunded': 'مسترد'
        }
        return status_labels.get(obj.status, obj.status)
    
    def get_method_display(self, obj):
        """Get human readable payment method"""
        method_labels = {
            'cod': 'الدفع عند الاستلام',
            'card': 'بطاقة ائتمانية',
            'transfer': 'تحويل بنكي',
            'ccp': 'CCP',
            'edahabia': 'Edahabia',
            'cib': 'CIB',
            'wallet': 'محفظة إلكترونية'
        }
        return method_labels.get(obj.method, obj.method)
    
    def validate_amount(self, value):
        """Validate payment amount"""
        if value <= 0:
            raise serializers.ValidationError("المبلغ يجب أن يكون أكبر من صفر")
        return value
    
    def validate_status(self, value):
        """Validate payment status"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"الحالة يجب أن تكون واحدة من: {', '.join(valid_statuses)}")
        return value
    
    def validate_method(self, value):
        """Validate payment method"""
        valid_methods = ['cod', 'card', 'transfer', 'ccp', 'edahabia', 'cib', 'wallet']
        if value not in valid_methods:
            raise serializers.ValidationError(f"طريقة الدفع يجب أن تكون واحدة من: {', '.join(valid_methods)}")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # If payment is completed, transaction_id should be present for non-COD payments
        if data.get('status') == 'completed' and data.get('method') != 'cod':
            if not data.get('transaction_id'):
                raise serializers.ValidationError(
                    "معرف المعاملة مطلوب للمدفوعات المكتملة غير النقدية"
                )
        
        # Validate amount against order total if order is provided
        order = data.get('order') or (self.instance and self.instance.order)
        if order and 'amount' in data:
            if data['amount'] > order.total_amount:
                raise serializers.ValidationError(
                    f"المبلغ لا يمكن أن يتجاوز إجمالي الطلب ({order.total_amount})"
                )
        
        return data
    
    def create(self, validated_data):
        """Create payment with additional validation"""
        order = validated_data['order']
        
        # Check if payment already exists for this order (excluding COD)
        if validated_data.get('method') != 'cod':
            existing_payment = Payment.objects.filter(
                order=order,
                method=validated_data.get('method'),
                status__in=['pending', 'processing', 'completed']
            ).first()
            
            if existing_payment:
                raise serializers.ValidationError(
                    f"يوجد دفع بالفعل لهذا الطلب باستخدام {validated_data.get('method')}"
                )
        
        # Set default amount if not provided
        if 'amount' not in validated_data:
            validated_data['amount'] = order.total_amount
        
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    customer_info = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    timeline = OrderTimelineSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    is_paid = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    calculated_total = serializers.SerializerMethodField()
    wilaya_name = serializers.CharField(source='wilaya.name_ar', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'phone', 'email',
            'shipping_address', 'wilaya', 'wilaya_name', 'subtotal', 'shipping_cost',
            'tax', 'discount_amount', 'total_amount', 'calculated_total',
            'status', 'payment_method', 'payment_status', 'notes',
            'sync_status', 'erpnext_sales_order_id', 'sync_error', 'last_synced_at',
            'created_at', 'updated_at', 'customer_info', 'items', 'timeline',
            'payments', 'is_paid', 'can_cancel'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_customer_info(self, obj):
        """Get customer information"""
        return {
            'name': obj.customer_name,
            'email': obj.email,
            'phone': obj.phone,
            'address': obj.shipping_address,
            'wilaya': obj.wilaya.name_ar if obj.wilaya else None
        }
    
    def get_is_paid(self, obj):
        """Check if order is paid"""
        return obj.payment_status
    
    def get_can_cancel(self, obj):
        """Check if order can be cancelled"""
        return obj.status in ['pending', 'confirmed']
    
    def get_calculated_total(self, obj):
        """Calculate total amount based on subtotal, shipping, tax, and discount"""
        return obj.calculate_total_amount()


class OrderCreateSerializer(serializers.ModelSerializer):
    """Order creation serializer"""
    items = OrderItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'user', 'customer_name', 'phone', 'email',
            'shipping_address', 'wilaya', 'subtotal', 'shipping_cost',
            'tax', 'discount_amount', 'payment_method', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        """Create order with items and calculate total_amount"""
        items_data = validated_data.pop('items', [])
        
        # Calculate subtotal from items if not provided
        if not validated_data.get('subtotal') and items_data:
            subtotal = sum(item['price'] * item['quantity'] for item in items_data)
            validated_data['subtotal'] = subtotal
        
        # Calculate total amount
        subtotal = validated_data.get('subtotal', 0)
        shipping_cost = validated_data.get('shipping_cost', 0)
        tax = validated_data.get('tax', 0)
        discount_amount = validated_data.get('discount_amount', 0)
        validated_data['total_amount'] = subtotal + shipping_cost + tax - discount_amount
        
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Order update serializer"""
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'notes', 'sync_status',
            'erpnext_sales_order_id', 'sync_error', 'last_synced_at'
        ]
    
    def update(self, instance, validated_data):
        """Update order"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
