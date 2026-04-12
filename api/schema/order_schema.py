"""
Order Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Sum, Count, Avg
from decimal import Decimal
from api.models.order import Order, OrderItem, OrderTimeline, Payment
from api.models.shipping import Shipping
from api.models.coupon import Coupon


class CouponType(DjangoObjectType):
    """Basic coupon type for order schema"""
    
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'name', 'discount_type', 'discount_value', 'is_active', 'used_count']


class OrderType(DjangoObjectType):
    """Enhanced order type"""
    id = graphene.ID(required=True)
    order_number = String()
    
    # Customer information
    user = Field(lambda: UserType)
    customer_name = String()
    phone = String()
    email = String()
    
    # Shipping information
    shipping_address = String()
    wilaya = Field(lambda: ShippingType)
    wilaya_name = String()
    shipping_method = Field(lambda: ShippingMethodType)
    shipping_method_name = String()
    
    # Financial information
    subtotal = Float()
    shipping_cost = Float()
    tax = Float()
    discount_amount = Float()
    total_amount = Float()
    calculated_total = Float()
    
    # Status and workflow
    status = String()
    payment_method = String()
    payment_status = Boolean()
    is_paid = Boolean()
    
    # ERPNext synchronization
    sync_status = String()
    erpnext_sales_order_id = String()
    sync_error = String()
    last_synced_at = DateTime()
    
    # Notes
    notes = String()
    
    # Relations
    items = List(lambda: OrderItemType)
    payments = List(lambda: PaymentType)
    timeline = List(lambda: OrderTimelineType)
    coupon = Field(lambda: CouponType)
    
    # Computed fields
    can_cancel = Boolean()
    customer_info = JSONString()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order_number': ['exact', 'icontains'],
            'status': ['exact'],
            'payment_status': ['exact'],
            'user': ['exact'],
            'wilaya': ['exact'],
            'payment_method': ['exact'],
            'sync_status': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        """Optimize queryset with select_related and prefetch_related"""
        return queryset.select_related(
            'user',
            'wilaya',
            'shipping_method',
            'coupon'
        ).prefetch_related(
            'items__product',
            'items__material',
            'timeline__user'
        ).only(
            'id', 'order_number', 'user_id', 'customer_name', 'phone', 'email',
            'shipping_address', 'wilaya_id', 'shipping_method_id', 'subtotal',
            'shipping_cost', 'tax', 'discount_amount', 'total_amount',
            'status', 'payment_method', 'payment_status', 'sync_status',
            'erpnext_sales_order_id', 'sync_error', 'last_synced_at', 'notes',
            'coupon_id', 'created_at', 'updated_at'
        )

    def resolve_is_paid(self, info):
        """Check if order is paid"""
        return self.payment_status

    def resolve_can_cancel(self, info):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']

    def resolve_wilaya_name(self, info):
        """Get wilaya name"""
        return self.wilaya.name_ar if self.wilaya else None

    def resolve_shipping_method_name(self, info):
        """Get shipping method name"""
        return self.shipping_method.name if self.shipping_method else None

    def resolve_calculated_total(self, info):
        """Calculate total amount based on subtotal, shipping, tax, and discount"""
        return self.calculate_total_amount()

    def resolve_customer_info(self, info):
        """Get customer information"""
        return {
            'name': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.shipping_address,
            'wilaya': self.wilaya.name_ar if self.wilaya else None
        }

    def resolve_timeline(self, info):
        """Get order timeline sorted by timestamp (newest first)"""
        return self.timeline.all().order_by('-timestamp')


class OrderItemType(DjangoObjectType):
    """Order item type with enhanced fields"""
    id = graphene.ID(required=True)
    order = Field(OrderType)
    product = Field(lambda: ProductType)
    product_name = String()
    
    # Material and customization
    material = Field(lambda: MaterialType)
    material_name = String()
    width = Float()
    height = Float()
    dimension_unit = String()
    marble_texture = String()
    custom_design = String()
    
    # Pricing with price locking
    quantity = Int()
    price = Float()
    subtotal = Float()
    original_product_price = Float()
    area_cm2 = Float()
    area_m2 = Float()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = OrderItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'product': ['exact'],
            'material': ['exact'],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        """Optimize queryset with select_related"""
        return queryset.select_related(
            'order',
            'product',
            'material'
        ).only(
            'id', 'order_id', 'product_id', 'material_id', 'width', 'height',
            'dimension_unit', 'marble_texture', 'custom_design', 'quantity',
            'price', 'created_at', 'updated_at'
        )

    def resolve_product_name(self, info):
        """Get product name"""
        return self.product.name_ar if self.product else None

    def resolve_material_name(self, info):
        """Get material name"""
        return self.material.name_ar if self.material else None

    def resolve_subtotal(self, info):
        """Calculate subtotal for this item"""
        return self.price * self.quantity
    
    def resolve_original_product_price(self, info):
        """Get original product price at time of order"""
        return self.product.base_price if self.product else None
    
    def resolve_area_cm2(self, info):
        """Calculate area in cm²"""
        return self.width * self.height if self.width and self.height else None
    
    def resolve_area_m2(self, info):
        """Calculate area in m²"""
        if self.width and self.height:
            return (self.width * self.height) / 10000  # Convert cm² to m²
        return None


class OrderTimelineType(DjangoObjectType):
    """Order timeline type"""
    id = graphene.ID(required=True)
    order = Field(OrderType)
    status = String()
    note = String()
    
    # User tracking
    user = Field(lambda: UserType)
    user_name = String()
    
    timestamp = DateTime()

    class Meta:
        model = OrderTimeline
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'status': ['exact'],
            'timestamp': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_user_name(self, info):
        """Get user name"""
        return self.user.username if self.user else None


class PaymentType(DjangoObjectType):
    """Payment type"""
    id = graphene.ID(required=True)
    order = Field(OrderType)
    
    # Payment details
    amount = Float()
    method = String()
    
    # Status and tracking
    status = String()
    transaction_id = String()
    
    # Gateway response
    gateway_response = JSONString()
    
    # Dates
    created_at = DateTime()
    updated_at = DateTime()
    
    is_successful = Boolean()

    class Meta:
        model = Payment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'status': ['exact'],
            'method': ['exact'],
            'transaction_id': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_successful(self, info):
        """Check if payment was successful"""
        return self.status == 'completed'


# Input Types
class OrderInput(graphene.InputObjectType):
    """Input for order creation"""
    user_id = ID()
    customer_name = String(required=True)
    phone = String(required=True)
    email = String()
    shipping_address = String(required=True)
    wilaya_id = ID()
    shipping_method_id = ID()
    subtotal = Float()
    shipping_cost = Float(default_value=0)
    tax = Float(default_value=0)
    discount_amount = Float(default_value=0)
    coupon_code = String()
    payment_method = String(default_value='cod')
    notes = String()
    
    # ERPNext synchronization
    sync_status = String(default_value='pending')
    erpnext_sales_order_id = String()
    sync_error = String()
    last_synced_at = DateTime()


class OrderItemInput(graphene.InputObjectType):
    """Input for order item"""
    product_id = ID(required=True)
    material_id = ID()
    width = Float(required=True)
    height = Float(required=True)
    dimension_unit = String(default_value='cm')
    marble_texture = String()
    custom_design = String()
    quantity = Int(default_value=1)
    price = Float(required=True)


class PaymentInput(graphene.InputObjectType):
    """Input for payment processing"""
    order_id = ID(required=True)
    amount = Float()
    method = String()
    gateway = String()
    transaction_id = String()
    gateway_response = JSONString()


# Mutations
class CreateOrder(Mutation):
    """Create a new order"""
    
    class Arguments:
        input = OrderInput(required=True)
        items = List(OrderItemInput, required=True)

    success = Boolean()
    message = String()
    order = Field(OrderType)
    errors = List(String)

    def mutate(self, info, input, items):
        try:
            from api.models.order import Order, OrderItem
            from api.models.product import Product, Material
            from api.models.shipping import Shipping
            from api.models.coupon import Coupon
            from django.contrib.auth.models import User
            
            user = info.context.user
            authenticated_user = user if user.is_authenticated else None
            
            # Get user from input if provided
            if input.get('user_id'):
                try:
                    authenticated_user = User.objects.get(id=input['user_id'])
                except User.DoesNotExist:
                    return CreateOrder(
                        success=False,
                        message="User not found",
                        errors=["User not found"]
                    )
            
            # Get shipping info
            wilaya = None
            if input.get('wilaya_id'):
                try:
                    wilaya = Shipping.objects.get(id=input['wilaya_id'])
                except Shipping.DoesNotExist:
                    return CreateOrder(
                        success=False,
                        message="Wilaya not found",
                        errors=["Wilaya not found"]
                    )
            
            # Get shipping method
            shipping_method = None
            if input.get('shipping_method_id'):
                try:
                    from api.models.shipping import ShippingMethod
                    shipping_method = ShippingMethod.objects.get(id=input['shipping_method_id'])
                except ShippingMethod.DoesNotExist:
                    return CreateOrder(
                        success=False,
                        message="Shipping method not found",
                        errors=["Shipping method not found"]
                    )
            
            # Calculate subtotal from items if not provided
            calculated_subtotal = 0
            for item_data in items:
                calculated_subtotal += item_data['price'] * item_data['quantity']
            
            subtotal = input.get('subtotal') or calculated_subtotal
            
            # Calculate shipping cost based on shipping method to prevent tampering
            if shipping_method:
                shipping_cost = shipping_method.base_cost
            else:
                shipping_cost = input.get('shipping_cost', 0)
            
            tax = input.get('tax', 0)
            discount_amount = input.get('discount_amount', 0)
            
            # Handle coupon validation and discount calculation
            coupon = None
            coupon_discount = 0
            
            if input.get('coupon_code'):
                try:
                    coupon = Coupon.objects.get_coupon_by_code(input['coupon_code'])
                    if not coupon:
                        return CreateOrder(
                            success=False,
                            message="Invalid coupon code",
                            errors=["Coupon not found"]
                        )
                    
                    # Validate coupon
                    is_valid, message = coupon.is_valid(
                        user=authenticated_user, 
                        order_value=subtotal
                    )
                    
                    if not is_valid:
                        return CreateOrder(
                            success=False,
                            message=f"Coupon validation failed: {message}",
                            errors=[message]
                        )
                    
                    # Calculate discount
                    coupon_discount = coupon.calculate_discount(subtotal)
                    discount_amount += coupon_discount
                    
                except Exception as e:
                    return CreateOrder(
                        success=False,
                        message=f"Coupon processing error: {str(e)}",
                        errors=[str(e)]
                    )
            
            total_amount = subtotal + shipping_cost + tax - discount_amount
            
            # Ensure total is not negative
            total_amount = max(total_amount, 0)
            
            # Create order
            order = Order.objects.create(
                user=authenticated_user,
                customer_name=input.customer_name,
                phone=input.phone,
                email=input.get('email'),
                shipping_address=input.shipping_address,
                wilaya=wilaya,
                shipping_method=shipping_method,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                discount_amount=discount_amount,
                total_amount=total_amount,
                payment_method=input.get('payment_method', 'cod'),
                notes=input.get('notes'),
                coupon=coupon,
                sync_status=input.get('sync_status', 'pending'),
                erpnext_sales_order_id=input.get('erpnext_sales_order_id'),
                sync_error=input.get('sync_error'),
                last_synced_at=input.get('last_synced_at')
            )
            
            # Create order items
            for item_data in items:
                product = Product.objects.get(id=item_data['product_id'])
                material = None
                if item_data.get('material_id'):
                    material = Material.objects.get(id=item_data['material_id'])
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    material=material,
                    width=item_data['width'],
                    height=item_data['height'],
                    dimension_unit=item_data.get('dimension_unit', 'cm'),
                    marble_texture=item_data.get('marble_texture'),
                    custom_design=item_data.get('custom_design'),
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
            
            # Increment coupon usage if coupon was used
            if coupon:
                coupon.increment_usage(user=authenticated_user, order=order)
            
            return CreateOrder(
                success=True,
                message="Order created successfully",
                order=order
            )
            
        except Product.DoesNotExist:
            return CreateOrder(
                success=False,
                message="Product not found",
                errors=["One or more products not found"]
            )
        except Material.DoesNotExist:
            return CreateOrder(
                success=False,
                message="Material not found",
                errors=["One or more materials not found"]
            )
        except Exception as e:
            return CreateOrder(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateOrderStatus(Mutation):
    """Update order status"""
    
    class Arguments:
        order_id = ID(required=True)
        status = String(required=True)
        note = String()
        tracking_number = String()
        
    success = Boolean()
    message = String()
    order = Field(OrderType)
    errors = List(String)

    def mutate(self, info, order_id, status, note=None, tracking_number=None):
        try:
            order = Order.objects.get(id=order_id)
            
            # Update status
            order.status = status
            
            # Add status to timeline
            OrderTimeline.objects.create(
                order=order,
                status=status,
                title=f"Order {status}",
                note=note,
                user=info.context.user
            )
            
            # Update tracking if provided
            if tracking_number:
                order.tracking_number = tracking_number
            
            # Update timestamps based on status
            if status == 'shipped':
                order.shipped_at = timezone.now()
            elif status == 'delivered':
                order.delivered_at = timezone.now()
            elif status == 'cancelled':
                order.cancelled_at = timezone.now()
            
            order.save()
            
            return UpdateOrderStatus(
                success=True,
                message="Order status updated successfully",
                order=order
            )
            
        except Order.DoesNotExist:
            return UpdateOrderStatus(
                success=False,
                message="Order not found",
                errors=["Order not found"]
            )
        except Exception as e:
            return UpdateOrderStatus(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CancelOrder(Mutation):
    """Cancel an order"""
    
    class Arguments:
        order_id = ID(required=True)
        reason = String()

    success = Boolean()
    message = String()
    order = Field(OrderType)
    errors = List(String)

    def mutate(self, info, order_id, reason=None):
        try:
            order = Order.objects.get(id=order_id)
            
            if not order.can_cancel:
                return CancelOrder(
                    success=False,
                    message="Order cannot be cancelled",
                    errors=["Order cannot be cancelled"]
                )
            
            order.cancel(reason)
            
            return CancelOrder(
                success=True,
                message="Order cancelled successfully",
                order=order
            )
            
        except Order.DoesNotExist:
            return CancelOrder(
                success=False,
                message="Order not found",
                errors=["Order not found"]
            )
        except Exception as e:
            return CancelOrder(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class BulkCreateOrderItems(Mutation):
    """Bulk create order items for an existing order"""
    
    class Arguments:
        order_id = ID(required=True)
        items = List(OrderItemInput, required=True)

    success = Boolean()
    message = String()
    order_items = List(OrderItemType)
    errors = List(String)

    def mutate(self, info, order_id, items):
        try:
            from api.models.order import Order, OrderItem
            from api.models.product import Product, Material
            
            # Get the order
            order = Order.objects.get(id=order_id)
            
            created_items = []
            errors = []
            
            for item_data in items:
                try:
                    # Validate product exists
                    product = Product.objects.get(id=item_data['product_id'])
                    
                    # Validate material if provided
                    material = None
                    if item_data.get('material_id'):
                        material = Material.objects.get(id=item_data['material_id'])
                    
                    # Calculate price if not provided
                    if 'price' not in item_data:
                        width = item_data.get('width', 1)
                        height = item_data.get('height', 1)
                        area = width * height / 10000  # Convert cm² to m²
                        
                        if material and hasattr(material, 'price_per_m2'):
                            item_data['price'] = product.base_price + (material.price_per_m2 * area)
                        else:
                            item_data['price'] = product.base_price
                    
                    # Create order item
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        material=material,
                        width=item_data['width'],
                        height=item_data['height'],
                        dimension_unit=item_data.get('dimension_unit', 'cm'),
                        marble_texture=item_data.get('marble_texture'),
                        custom_design=item_data.get('custom_design'),
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    
                    created_items.append(order_item)
                    
                except Product.DoesNotExist:
                    errors.append(f"Product with ID {item_data['product_id']} not found")
                except Material.DoesNotExist:
                    errors.append(f"Material with ID {item_data.get('material_id')} not found")
                except Exception as e:
                    errors.append(f"Error creating item: {str(e)}")
            
            # Update order subtotal
            if created_items:
                new_subtotal = sum(item.price * item.quantity for item in created_items)
                existing_subtotal = sum(item.price * item.quantity for item in order.items.all())
                order.subtotal = existing_subtotal + new_subtotal
                order.total_amount = order.subtotal + order.shipping_cost + order.tax - order.discount_amount
                order.save()
            
            return BulkCreateOrderItems(
                success=len(created_items) > 0,
                message=f"Created {len(created_items)} order items successfully",
                order_items=created_items,
                errors=errors if errors else None
            )
            
        except Order.DoesNotExist:
            return BulkCreateOrderItems(
                success=False,
                message="Order not found",
                errors=["Order not found"]
            )
        except Exception as e:
            return BulkCreateOrderItems(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreatePayment(Mutation):
    """Create a new payment record"""
    
    class Arguments:
        input = PaymentInput(required=True)

    success = Boolean()
    message = String()
    payment = Field(PaymentType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.order import Order, Payment
            
            # Get order
            order = Order.objects.get(id=input['order_id'])
            
            # Create payment
            payment = Payment.objects.create(
                order=order,
                amount=input.get('amount', order.total_amount),
                method=input.get('method', order.payment_method),
                status=input.get('status', 'pending'),
                transaction_id=input.get('transaction_id'),
                gateway_response=input.get('gateway_response', {})
            )
            
            # Update order payment status if payment is successful
            if payment.status == 'completed':
                order.payment_status = True
                order.save()
            
            return CreatePayment(
                success=True,
                message="Payment recorded successfully",
                payment=payment
            )
            
        except Order.DoesNotExist:
            return CreatePayment(
                success=False,
                message="Order not found",
                errors=["Order not found"]
            )
        except Exception as e:
            return CreatePayment(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdatePaymentStatus(Mutation):
    """Update payment status"""
    
    class Arguments:
        payment_id = ID(required=True)
        status = String(required=True)
        transaction_id = String()
        gateway_response = JSONString()

    success = Boolean()
    message = String()
    payment = Field(PaymentType)
    errors = List(String)

    def mutate(self, info, payment_id, status, transaction_id=None, gateway_response=None):
        try:
            from api.models.order import Payment
            
            payment = Payment.objects.get(id=payment_id)
            
            # Update payment fields
            payment.status = status
            if transaction_id:
                payment.transaction_id = transaction_id
            if gateway_response:
                payment.gateway_response = gateway_response
            
            payment.save()
            
            # Update order payment status if payment is successful
            if status == 'completed':
                payment.order.payment_status = True
                payment.order.save()
            
            return UpdatePaymentStatus(
                success=True,
                message="Payment status updated successfully",
                payment=payment
            )
            
        except Payment.DoesNotExist:
            return UpdatePaymentStatus(
                success=False,
                message="Payment not found",
                errors=["Payment not found"]
            )
        except Exception as e:
            return UpdatePaymentStatus(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class OrderQuery(ObjectType):
    """Order queries"""
    
    orders = List(OrderType)
    order = Field(OrderType, id=ID(required=True))
    orders_connection = DjangoFilterConnectionField(OrderType)
    my_orders = List(OrderType)
    
    def resolve_orders(self, info):
        """Get all orders (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Order.objects.all()
        return []
    
    def resolve_order(self, info, id):
        """Get order by ID"""
        user = info.context.user
        try:
            order = Order.objects.get(id=id)
            # Check if user can access this order
            if user.is_authenticated and (
                user.is_staff or 
                order.user == user
            ):
                return order
            return None
        except Order.DoesNotExist:
            return None


# Node Classes from core/schema.py
class ShippingNode(DjangoObjectType):
    """Shipping node with enhanced filtering"""
    class Meta:
        model = models.Shipping
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'home_delivery_price': ['lt', 'lte', 'gt', 'gte'],
            'stop_desk_price': ['lt', 'lte', 'gt', 'gte'],
        }


class OrderNode(DjangoObjectType, IsAuthenticatedMixin):
    """Enhanced order node with relationships"""
    user = Field('UserNode')
    items = List('OrderItemNode')
    payments = List('PaymentNode')
    shipping = Field('ShippingNode')
    
    class Meta:
        model = models.Order
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order_number': ['exact', 'icontains'],
            'status': ['exact'],
            'user': ['exact'],
            'created_at': ['lt', 'lte', 'gt', 'gte'],
        }


class OrderItemNode(DjangoObjectType):
    """Order item node with product details"""
    product = Field('ProductNode')
    material = Field('MaterialNode')
    
    class Meta:
        model = models.OrderItem
        interfaces = (relay.Node,)
        fields = '__all__'


class OrderTimelineNode(DjangoObjectType):
    """Order timeline node for tracking"""
    class Meta:
        model = models.OrderTimeline
        interfaces = (relay.Node,)
        fields = '__all__'


class PaymentNode(DjangoObjectType):
    """Payment node with enhanced filtering"""
    class Meta:
        model = models.Payment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'status': ['exact'],
            'payment_method': ['exact'],
            'amount': ['lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_my_orders(self, info):
        """Get current user's orders"""
        user = info.context.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return []


# Mutation Class
class OrderMutation(ObjectType):
    """Order mutations"""
    
    create_order = CreateOrder.Field()
    update_order_status = UpdateOrderStatus.Field()
    cancel_order = CancelOrder.Field()
    bulk_create_order_items = BulkCreateOrderItems.Field()
    create_payment = CreatePayment.Field()
    update_payment_status = UpdatePaymentStatus.Field()
