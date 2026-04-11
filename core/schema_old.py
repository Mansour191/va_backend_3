from graphene import relay, ObjectType, Schema, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

# Import all new schemas from api package
from api.schema import Query as APIQuery, Mutation as APIMutation

User = get_user_model()


# Authentication and Permission Mixins
class IsAuthenticatedMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()


class IsStaffMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return queryset
        return queryset.none()


class UserNode(DjangoObjectType):
    class Meta:
        model = models.User
        interfaces = (relay.Node,)
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    
    # Add profile resolver
    profile = Field(UserProfileNode)
    
    def resolve_profile(self, info):
        try:
            return self.profile
        except models.UserProfile.DoesNotExist:
            return None


class UserProfileNode(DjangoObjectType):
    class Meta:
        model = models.UserProfile
        interfaces = (relay.Node,)
        fields = '__all__'


class CategoryNode(DjangoObjectType):
    class Meta:
        model = models.Category
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'parent': ['exact'],
        }
    
    # Add custom resolvers for tree structure
    children = List('self')
    level = Int()
    
    def resolve_children(self, info):
        """Get direct children of this category"""
        return models.Category.objects.filter(parent=self, is_active=True)
    
    def resolve_level(self, info):
        """Calculate the level of this category in the tree"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level


class MaterialNode(DjangoObjectType):
    class Meta:
        model = models.Material
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_premium': ['exact'],
        }


class ProductNode(DjangoObjectType):
    images = List('ProductImageNode')
    variants = List('ProductVariantNode')
    available_materials = List('ProductMaterialNode')
    category = Field('CategoryNode')
    
    class Meta:
        model = models.Product
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'is_featured': ['exact'],
            'is_new': ['exact'],
            'on_sale': ['exact'],
            'category': ['exact'],
            'base_price': ['lt', 'lte', 'gt', 'gte'],
        }


class ProductImageNode(DjangoObjectType):
    class Meta:
        model = models.ProductImage
        interfaces = (relay.Node,)
        fields = '__all__'


class ProductVariantNode(DjangoObjectType):
    class Meta:
        model = models.ProductVariant
        interfaces = (relay.Node,)
        fields = '__all__'


class ProductMaterialNode(DjangoObjectType):
    material = Field('MaterialNode')
    
    class Meta:
        model = models.ProductMaterial
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'material': ['exact'],
            'is_active': ['exact'],
        }


class ShippingNode(DjangoObjectType):
    class Meta:
        model = models.Shipping
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'wilaya_id': ['exact'],
            'wilaya_code': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'home_delivery_price': ['lt', 'lte', 'gt', 'gte'],
            'stop_desk_price': ['lt', 'lte', 'gt', 'gte'],
        }
    
    # Custom resolvers
    delivery_price = Field(Float, delivery_type=String(default_value='home'))
    is_free_shipping_eligible = Field(Boolean, order_total=Float())
    
    def resolve_delivery_price(self, info, delivery_type='home'):
        """Get delivery price based on type"""
        return self.get_delivery_price(delivery_type)
    
    def resolve_is_free_shipping_eligible(self, info, order_total=None):
        """Check if order qualifies for free shipping"""
        if order_total is not None:
            return self.is_free_shipping_eligible(order_total)
        return False


class OrderNode(DjangoObjectType, IsAuthenticatedMixin):
    user = Field(UserNode)
    items = List('OrderItemNode')
    payments = List('PaymentNode')
    timeline = List('OrderTimelineNode')
    wilaya = Field('ShippingNode')
    
    class Meta:
        model = models.Order
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order_number': ['exact', 'icontains'],
            'status': ['exact'],
            'payment_method': ['exact'],
            'payment_status': ['exact'],
            'user': ['exact'],
        }


class OrderItemNode(DjangoObjectType):
    class Meta:
        model = models.OrderItem
        interfaces = (relay.Node,)
        fields = '__all__'


class OrderTimelineNode(DjangoObjectType):
    class Meta:
        model = models.OrderTimeline
        interfaces = (relay.Node,)
        fields = '__all__'


class PaymentNode(DjangoObjectType):
    class Meta:
        model = models.Payment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'status': ['exact'],
            'method': ['exact'],
            'order': ['exact'],
        }


class CouponNode(DjangoObjectType):
    class Meta:
        model = models.Coupon
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'code': ['exact'],
            'is_active': ['exact'],
        }


class CartItemNode(DjangoObjectType, IsAuthenticatedMixin):
    user = Field(UserNode)
    product = Field(ProductNode)
    material = Field(MaterialNode)
    wilaya = Field('ShippingNode')
    applied_coupon = Field('CouponNode')
    
    # Enhanced product details for better UI integration
    product_details = Field(JSONString)
    
    # Computed fields
    subtotal = Field(Float)
    total_with_discount = Field(Float)
    final_total = Field(Float)
    is_available = Field(Boolean)
    max_quantity = Field(Int)
    
    # Real-time pricing fields
    current_unit_price = Field(Float)
    current_material_price = Field(Float)
    price_changed = Field(Boolean)
    
    class Meta:
        model = models.CartItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
            'material': ['exact'],
            'delivery_type': ['exact'],
        }
    
    def resolve_subtotal(self, info):
        """Calculate subtotal for this cart item"""
        return self.subtotal
    
    def resolve_total_with_discount(self, info):
        """Calculate total after discount"""
        return self.total_with_discount
    
    def resolve_final_total(self, info):
        """Calculate final total including shipping"""
        return self.final_total
    
    def resolve_is_available(self, info):
        """Check if product is available"""
        return self.is_available
    
    def resolve_max_quantity(self, info):
        """Get maximum quantity available"""
        return self.max_quantity
    
    def resolve_product_details(self, info):
        """Get enhanced product details for UI"""
        return {
            'id': self.product.id,
            'name_ar': self.product.name_ar,
            'name_en': self.product.name_en,
            'slug': self.product.slug,
            'base_price': float(self.product.base_price),
            'stock': self.product.stock,
            'is_active': self.product.is_active,
            'images': [
                {
                    'id': img.id,
                    'image_url': img.image_url,
                    'is_main': img.is_main
                } for img in self.product.images.all()
            ]
        }
    
    def resolve_current_unit_price(self, info):
        """Get current unit price from product"""
        return float(self.product.base_price)
    
    def resolve_current_material_price(self, info):
        """Get current material price"""
        if self.material:
            if self.width and self.height:
                area_m2 = (float(self.width) * float(self.height)) / 10000
                return float(self.material.price_per_m2 * area_m2)
            return float(self.material.price_per_m2)
        return 0.0
    
    def resolve_price_changed(self, info):
        """Check if price has changed since cart item was created"""
        current_unit = float(self.product.base_price)
        current_material = self.resolve_current_material_price(info)
        
        return (current_unit != float(self.unit_price) or 
                current_material != float(self.material_price))


class WishlistNode(DjangoObjectType, IsAuthenticatedMixin):
    user = Field(UserNode)
    product = Field('ProductNode')
    
    # Enhanced product details
    product_details = Field(JSONString)
    
    # Computed fields
    is_available = Field(Boolean)
    is_in_stock = Field(Boolean)
    current_price = Field(Float)
    has_discount = Field(Boolean)
    discount_percentage = Field(Int)
    discounted_price = Field(Float)
    savings_amount = Field(Float)
    days_in_wishlist = Field(Int)
    
    class Meta:
        model = models.Wishlist
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
            'priority': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_product_details(self, info):
        """Get enhanced product details"""
        return {
            'id': self.product.id,
            'name_ar': self.product.name_ar,
            'name_en': self.product.name_en,
            'slug': self.product.slug,
            'base_price': float(self.product.base_price),
            'stock': self.product.stock,
            'is_active': self.product.is_active,
            'on_sale': self.product.on_sale,
            'discount_percent': self.product.discount_percent,
            'images': [
                {
                    'id': img.id,
                    'image_url': img.image_url,
                    'is_main': img.is_main
                } for img in self.product.images.all()
            ]
        }
    
    def resolve_is_available(self, info):
        """Check if product is available"""
        return self.product.is_active and self.product.stock > 0
    
    def resolve_is_in_stock(self, info):
        """Check if product is in stock"""
        return self.product.stock > 0
    
    def resolve_current_price(self, info):
        """Get current product price"""
        return float(self.product.base_price)
    
    def resolve_has_discount(self, info):
        """Check if product has discount"""
        return self.product.on_sale and self.product.discount_percent > 0
    
    def resolve_discount_percentage(self, info):
        """Get discount percentage"""
        if self.product.on_sale and self.product.discount_percent:
            return self.product.discount_percent
        return 0
    
    def resolve_discounted_price(self, info):
        """Calculate discounted price"""
        if self.product.on_sale and self.product.discount_percent:
            return float(self.product.base_price * (1 - self.product.discount_percent / 100))
        return float(self.product.base_price)
    
    def resolve_savings_amount(self, info):
        """Calculate savings amount"""
        if self.product.on_sale and self.product.discount_percent:
            return float(self.product.base_price - self.resolve_discounted_price(info))
        return 0.0
    
    def resolve_days_in_wishlist(self, info):
        """Calculate days since added to wishlist"""
        if self.created_at:
            from django.utils import timezone
            return (timezone.now() - self.created_at).days
        return 0


class ReviewNode(DjangoObjectType):
    user = Field(UserNode)
    product = Field('ProductNode')
    
    class Meta:
        model = models.Review
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'rating': ['exact', 'gte', 'lte'],
            'is_verified': ['exact'],
            'product': ['exact'],
            'user': ['exact'],
        }


class ReviewReportNode(DjangoObjectType):
    class Meta:
        model = models.ReviewReport
        interfaces = (relay.Node,)
        fields = '__all__'


class DesignCategoryNode(DjangoObjectType):
    class Meta:
        model = models.DesignCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
        }


class DesignNode(DjangoObjectType):
    class Meta:
        model = models.Design
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'status': ['exact'],
            'is_featured': ['exact'],
            'is_active': ['exact'],
            'category': ['exact'],
        }


class NotificationNode(DjangoObjectType):
    class Meta:
        model = models.Notification
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'type': ['exact'],
            'is_read': ['exact'],
            'user': ['exact'],
        }


class AlertNode(DjangoObjectType):
    class Meta:
        model = models.Alert
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'type': ['exact'],
            'is_active': ['exact'],
            'user': ['exact'],
        }


class ERPNextSyncLogNode(DjangoObjectType):
    class Meta:
        model = models.ERPNextSyncLog
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'action': ['exact', 'icontains'],
            'status': ['exact'],
        }


class BehaviorTrackingNode(DjangoObjectType):
    class Meta:
        model = models.BehaviorTracking
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'action': ['exact', 'icontains'],
            'target_type': ['exact'],
            'user': ['exact'],
        }


class ForecastNode(DjangoObjectType):
    class Meta:
        model = models.Forecast
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'forecast_type': ['exact'],
            'period': ['exact'],
            'product': ['exact'],
        }


class CustomerSegmentNode(DjangoObjectType):
    class Meta:
        model = models.CustomerSegment
        interfaces = (relay.Node,)
        fields = '__all__'


class PricingEngineNode(DjangoObjectType):
    class Meta:
        model = models.PricingEngine
        interfaces = (relay.Node,)
        fields = '__all__'


class BlogCategoryNode(DjangoObjectType):
    class Meta:
        model = models.BlogCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
        }


class BlogPostNode(DjangoObjectType):
    class Meta:
        model = models.BlogPost
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'title_ar': ['exact', 'icontains'],
            'title_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_published': ['exact'],
            'category': ['exact'],
            'author': ['exact'],
        }


class ConversationHistoryNode(DjangoObjectType):
    class Meta:
        model = models.ConversationHistory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'session_id': ['exact'],
            'role': ['exact'],
            'source': ['exact'],
        }


class DashboardSettingsNode(DjangoObjectType):
    class Meta:
        model = models.DashboardSettings
        interfaces = (relay.Node,)
        fields = '__all__'


class WishlistSettingsNode(DjangoObjectType):
    class Meta:
        model = models.WishlistSettings
        interfaces = (relay.Node,)
        fields = '__all__'


# Enhanced Mutations with Authentication and Permissions

# Input Types
class ProductInput(graphene.InputObjectType):
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String(required=True)
    description_ar = String()
    description_en = String()
    base_price = Float(required=True)
    cost = Float()
    category_id = Int()
    on_sale = Boolean()
    discount_percent = Int()
    is_featured = Boolean()
    is_new = Boolean()
    is_active = Boolean()
    stock = Int()
    weight = Float()
    dimensions = String()
    tags = List(String)
    seo_title = String()
    seo_description = String()


class OrderInput(graphene.InputObjectType):
    customer_name = String(required=True)
    phone = String(required=True)
    email = String()
    shipping_address = String(required=True)
    wilaya_id = String()
    payment_method = String()
    notes = String()
    items = List(lambda: OrderItemInput)


class OrderItemInput(graphene.InputObjectType):
    product_id = Int(required=True)
    material_id = Int()
    width = Float(required=True)
    height = Float(required=True)
    dimension_unit = String()
    marble_texture = String()
    custom_design = String()
    quantity = Int(default_value=1)


class CartItemInput(graphene.InputObjectType):
    product_id = Int(required=True)
    material_id = Int()
    quantity = Int(default_value=1)
    width = Float()
    height = Float()
    dimension_unit = String(default_value='cm')
    delivery_type = String(default_value='home')
    wilaya_id = String()
    options = JSONString()


class UpdateCartInput(graphene.InputObjectType):
    cart_item_id = Int(required=True)
    quantity = Int(required=True)


class ApplyCouponInput(graphene.InputObjectType):
    coupon_code = String(required=True)
    cart_item_ids = List(Int)  # Optional: apply to specific items


class SetShippingInput(graphene.InputObjectType):
    wilaya_id = String(required=True)
    delivery_type = String(default_value='home')
    cart_item_ids = List(Int)  # Optional: apply to specific items


class PaymentInput(graphene.InputObjectType):
    order_id = Int(required=True)
    amount = Float(required=True)
    method = String(required=True)
    transaction_id = String()


class ReviewInput(graphene.InputObjectType):
    product_id = Int(required=True)
    rating = Int(required=True)
    comment = String()


class CreateCategory(Mutation):
    class Arguments:
        name_ar = String(required=True)
        name_en = String(required=True)
        slug = String(required=True)
        description = String()
        icon = String()
        waste_percent = Float()
        image = String()
        parent_id = Int()

    category = Field(CategoryNode)
    success = Boolean()
    message = String()

    def mutate(self, info, name_ar, name_en, slug, **kwargs):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateCategory(success=False, message="Authentication and staff privileges required")
        
        try:
            category = models.Category.objects.create(
                name_ar=name_ar,
                name_en=name_en,
                slug=slug,
                **kwargs
            )
            return CreateCategory(category=category, success=True, message="Category created successfully")
        except Exception as e:
            return CreateCategory(success=False, message=str(e))


class CreateProduct(Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = Field(ProductNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateProduct(success=False, message="Authentication and staff privileges required")
        
        try:
            category = None
            if input.category_id:
                category = models.Category.objects.get(id=input.category_id)
            
            product = models.Product.objects.create(
                name_ar=input.name_ar,
                name_en=input.name_en,
                slug=input.slug,
                description_ar=input.description_ar,
                description_en=input.description_en,
                base_price=input.base_price,
                cost=input.cost or 0,
                category=category,
                on_sale=input.on_sale or False,
                discount_percent=input.discount_percent or 0,
                is_featured=input.is_featured or False,
                is_new=input.is_new or True,
                is_active=input.is_active or True,
                stock=input.stock or 0,
                weight=input.weight,
                dimensions=input.dimensions,
                tags=input.tags or [],
                seo_title=input.seo_title,
                seo_description=input.seo_description
            )
            
            return CreateProduct(product=product, success=True, message="Product created successfully")
        except Exception as e:
            return CreateProduct(success=False, message=str(e))


class CreateOrder(Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = Field(OrderNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateOrder(success=False, message="Authentication required")
        
        try:
            import uuid
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            wilaya = None
            if input.wilaya_id:
                wilaya = models.Shipping.objects.get(wilaya_id=input.wilaya_id)
            
            # Calculate totals
            subtotal = 0
            order_items = []
            
            for item_input in input.items:
                product = models.Product.objects.get(id=item_input.product_id)
                material = None
                if item_input.material_id:
                    material = models.Material.objects.get(id=item_input.material_id)
                
                # Calculate item price (simplified)
                item_price = product.base_price * item_input.quantity
                if material:
                    item_price += material.price_per_m2 * (item_input.width * item_input.height / 10000)  # Convert to m2
                
                subtotal += item_price
                order_items.append((product, material, item_input, item_price))
            
            # Calculate shipping and tax (simplified)
            shipping_cost = wilaya.home_delivery_price if wilaya else 0
            tax = subtotal * 0.19  # 19% tax
            total_amount = subtotal + shipping_cost + tax
            
            # Create order
            order = models.Order.objects.create(
                order_number=order_number,
                user=info.context.user,
                customer_name=input.customer_name,
                phone=input.phone,
                email=input.email,
                shipping_address=input.shipping_address,
                wilaya=wilaya,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                total_amount=total_amount,
                payment_method=input.payment_method or 'cod',
                notes=input.notes
            )
            
            # Create order items
            for product, material, item_input, item_price in order_items:
                models.OrderItem.objects.create(
                    order=order,
                    product=product,
                    material=material,
                    width=item_input.width,
                    height=item_input.height,
                    dimension_unit=item_input.dimension_unit or 'cm',
                    marble_texture=item_input.marble_texture,
                    custom_design=item_input.custom_design,
                    quantity=item_input.quantity,
                    price=item_price
                )
            
            return CreateOrder(order=order, success=True, message="Order created successfully")
        except Exception as e:
            return CreateOrder(success=False, message=str(e))


class ProcessPayment(Mutation):
    class Arguments:
        input = PaymentInput(required=True)

    payment = Field(PaymentNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return ProcessPayment(success=False, message="Authentication required")
        
        try:
            order = models.Order.objects.get(id=input.order_id)
            
            # Verify user owns the order or is staff
            if order.user != info.context.user and not info.context.user.is_staff:
                return ProcessPayment(success=False, message="Permission denied")
            
            # Create payment record
            payment = models.Payment.objects.create(
                order=order,
                amount=input.amount,
                method=input.method,
                status='completed',  # Simplified - in real app, this would be 'pending' then updated
                transaction_id=input.transaction_id
            )
            
            # Update order payment status
            if payment.amount >= order.total_amount:
                order.payment_status = True
                order.status = 'confirmed'
                order.save()
            
            return ProcessPayment(payment=payment, success=True, message="Payment processed successfully")
        except Exception as e:
            return ProcessPayment(success=False, message=str(e))


class AddToCart(Mutation):
    class Arguments:
        input = CartItemInput(required=True)

    cart_item = Field(CartItemNode)
    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)
    price_warnings = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            # For guest users, use session
            session_id = info.context.session.session_key or info.context.session.create()
        else:
            session_id = None
        
        try:
            product = models.Product.objects.get(id=input.product_id)
            
            # Enhanced stock validation
            if not product.is_active:
                return AddToCart(success=False, message="Product is not available")
            
            if product.stock < input.quantity:
                return AddToCart(
                    success=False, 
                    message=f"Only {product.stock} items available",
                    price_warnings={'available_stock': product.stock}
                )
            
            material = None
            if input.material_id:
                material = models.Material.objects.get(id=input.material_id)
            
            wilaya = None
            if input.wilaya_id:
                wilaya = models.Shipping.objects.get(wilaya_id=input.wilaya_id)
                if not wilaya.is_active:
                    return AddToCart(success=False, message="Shipping to this wilaya is not available")
            
            # Get or create cart item with enhanced defaults
            cart_item, created = models.CartItem.objects.get_or_create(
                user=user if user.is_authenticated else None,
                session_id=session_id if not user.is_authenticated else None,
                product=product,
                material=material,
                width=input.width,
                height=input.height,
                defaults={
                    'quantity': input.quantity,
                    'dimension_unit': input.dimension_unit or 'cm',
                    'delivery_type': input.delivery_type or 'home',
                    'wilaya': wilaya,
                    'options': input.options or {},
                    'unit_price': product.base_price,
                    'material_price': material.price_per_m2 if material else 0,
                }
            )
            
            if not created:
                # Update existing item with stock validation
                new_quantity = cart_item.quantity + input.quantity
                if new_quantity > product.stock:
                    return AddToCart(
                        success=False, 
                        message=f"Only {product.stock} items available",
                        price_warnings={'available_stock': product.stock}
                    )
                
                cart_item.quantity = new_quantity
                cart_item.save()
            
            # Calculate shipping cost
            if wilaya:
                cart_item.shipping_cost = cart_item.calculate_shipping_cost(wilaya, input.delivery_type or 'home')
                cart_item.save()
            
            # Get enhanced cart summary
            cart_items = models.CartItem.objects.filter(
                user=user if user.is_authenticated else None,
                session_id=session_id if not user.is_authenticated else None
            )
            
            # Check for price changes
            price_warnings = []
            for item in cart_items:
                current_unit_price = float(item.product.base_price)
                current_material_price = 0
                if item.material:
                    if item.width and item.height:
                        area_m2 = (float(item.width) * float(item.height)) / 10000
                        current_material_price = float(item.material.price_per_m2 * area_m2)
                    else:
                        current_material_price = float(item.material.price_per_m2)
                
                if (current_unit_price != float(item.unit_price) or 
                    current_material_price != float(item.material_price)):
                    price_warnings.append({
                        'cart_item_id': item.id,
                        'product_name': item.product.name_ar,
                        'old_unit_price': float(item.unit_price),
                        'new_unit_price': current_unit_price,
                        'old_material_price': float(item.material_price),
                        'new_material_price': current_material_price
                    })
            
            cart_summary = {
                'total_items': cart_items.count(),
                'subtotal': sum(float(item.subtotal) for item in cart_items),
                'discount_total': sum(float(item.discount_amount) + float(item.coupon_discount) for item in cart_items),
                'shipping_cost': sum(float(item.shipping_cost) for item in cart_items),
                'total': sum(float(item.final_total) for item in cart_items),
                'price_warnings': price_warnings
            }
            
            return AddToCart(
                cart_item=cart_item,
                success=True,
                message="Added to cart successfully",
                cart_summary=json.dumps(cart_summary),
                price_warnings=json.dumps(price_warnings) if price_warnings else None
            )
            
        except models.Product.DoesNotExist:
            return AddToCart(success=False, message="Product not found")
        except models.Material.DoesNotExist:
            return AddToCart(success=False, message="Material not found")
        except models.Shipping.DoesNotExist:
            return AddToCart(success=False, message="Wilaya not found")
        except Exception as e:
            return AddToCart(success=False, message=str(e))


class UpdateCartQuantity(Mutation):
    class Arguments:
        input = UpdateCartInput(required=True)

    cart_item = Field(CartItemNode)
    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateCartQuantity(success=False, message="Authentication required")
        
        try:
            cart_item = models.CartItem.objects.get(
                id=input.cart_item_id,
                user=user
            )
            
            # Check availability
            if input.quantity > cart_item.product.stock:
                return UpdateCartQuantity(
                    success=False, 
                    message=f"Only {cart_item.product.stock} items available"
                )
            
            if input.quantity <= 0:
                cart_item.delete()
                message = "Item removed from cart"
            else:
                cart_item.quantity = input.quantity
                cart_item.save()
                message = "Cart updated successfully"
            
            # Get updated cart summary
            cart_items = models.CartItem.objects.filter(user=user)
            cart_summary = {
                'total_items': cart_items.count(),
                'subtotal': sum(item.subtotal for item in cart_items),
                'shipping_cost': sum(item.shipping_cost for item in cart_items),
                'total': sum(item.final_total for item in cart_items)
            }
            
            return UpdateCartQuantity(
                cart_item=cart_item if input.quantity > 0 else None,
                success=True,
                message=message,
                cart_summary=json.dumps(cart_summary)
            )
            
        except models.CartItem.DoesNotExist:
            return UpdateCartQuantity(success=False, message="Cart item not found")
        except Exception as e:
            return UpdateCartQuantity(success=False, message=str(e))


class RemoveFromCart(Mutation):
    class Arguments:
        cart_item_id = Int(required=True)

    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, cart_item_id):
        user = info.context.user
        if not user.is_authenticated:
            return RemoveFromCart(success=False, message="Authentication required")
        
        try:
            cart_item = models.CartItem.objects.get(
                id=cart_item_id,
                user=user
            )
            cart_item.delete()
            
            # Get updated cart summary
            cart_items = models.CartItem.objects.filter(user=user)
            cart_summary = {
                'total_items': cart_items.count(),
                'subtotal': sum(item.subtotal for item in cart_items),
                'shipping_cost': sum(item.shipping_cost for item in cart_items),
                'total': sum(item.final_total for item in cart_items)
            }
            
            return RemoveFromCart(
                success=True,
                message="Item removed from cart",
                cart_summary=json.dumps(cart_summary)
            )
            
        except models.CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Cart item not found")
        except Exception as e:
            return RemoveFromCart(success=False, message=str(e))


class ApplyCoupon(Mutation):
    class Arguments:
        input = ApplyCouponInput(required=True)

    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return ApplyCoupon(success=False, message="Authentication required")
        
        try:
            coupon = models.Coupon.objects.get(
                code=input.coupon_code.upper(),
                is_active=True
            )
            
            # Check coupon validity
            from django.utils import timezone
            now = timezone.now()
            
            if coupon.valid_from and coupon.valid_from > now:
                return ApplyCoupon(success=False, message="Coupon is not yet valid")
            
            if coupon.valid_to and coupon.valid_to < now:
                return ApplyCoupon(success=False, message="Coupon has expired")
            
            # Get cart items to apply coupon to
            cart_items = models.CartItem.objects.filter(user=user)
            if input.cart_item_ids:
                cart_items = cart_items.filter(id__in=input.cart_item_ids)
            
            # Apply coupon to each item
            for cart_item in cart_items:
                cart_item.apply_coupon(coupon)
            
            # Get updated cart summary
            cart_summary = {
                'total_items': cart_items.count(),
                'subtotal': sum(item.subtotal for item in cart_items),
                'discount_total': sum(item.coupon_discount for item in cart_items),
                'shipping_cost': sum(item.shipping_cost for item in cart_items),
                'total': sum(item.final_total for item in cart_items)
            }
            
            return ApplyCoupon(
                success=True,
                message="Coupon applied successfully",
                cart_summary=json.dumps(cart_summary)
            )
            
        except models.Coupon.DoesNotExist:
            return ApplyCoupon(success=False, message="Invalid coupon code")
        except Exception as e:
            return ApplyCoupon(success=False, message=str(e))


class SetShipping(Mutation):
    class Arguments:
        input = SetShippingInput(required=True)

    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return SetShipping(success=False, message="Authentication required")
        
        try:
            wilaya = models.Shipping.objects.get(
                wilaya_id=input.wilaya_id,
                is_active=True
            )
            
            # Get cart items to update shipping for
            cart_items = models.CartItem.objects.filter(user=user)
            if input.cart_item_ids:
                cart_items = cart_items.filter(id__in=input.cart_item_ids)
            
            # Update shipping for each item
            for cart_item in cart_items:
                cart_item.wilaya = wilaya
                cart_item.delivery_type = input.delivery_type or 'home'
                cart_item.shipping_cost = cart_item.calculate_shipping_cost(
                    wilaya, 
                    input.delivery_type or 'home'
                )
                cart_item.save()
            
            # Get updated cart summary
            cart_summary = {
                'total_items': cart_items.count(),
                'subtotal': sum(item.subtotal for item in cart_items),
                'shipping_cost': sum(item.shipping_cost for item in cart_items),
                'total': sum(item.final_total for item in cart_items)
            }
            
            return SetShipping(
                success=True,
                message="Shipping updated successfully",
                cart_summary=json.dumps(cart_summary)
            )
            
        except models.Shipping.DoesNotExist:
            return SetShipping(success=False, message="Wilaya not available")
        except Exception as e:
            return SetShipping(success=False, message=str(e))


class ToggleWishlist(Mutation):
    """Toggle item in wishlist (add if not exists, remove if exists)"""
    
    class Arguments:
        product_id = Int(required=True)
        priority = Int(default_value=0)
        notes = String()
        notify_on_stock = Boolean(default_value=True)
        notify_on_discount = Boolean(default_value=True)
        notify_price_drop = Boolean(default_value=True)

    success = Boolean()
    message = String()
    is_in_wishlist = Field(Boolean)
    wishlist_item = Field(WishlistNode)
    wishlist_count = Field(Int)

    def mutate(self, info, product_id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return ToggleWishlist(
                success=False, 
                message="Authentication required",
                is_in_wishlist=False
            )
        
        try:
            with transaction.atomic():
                product = models.Product.objects.get(id=product_id)
                
                # Check if item already exists
                wishlist_item, created = models.Wishlist.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={
                        'priority': kwargs.get('priority', 0),
                        'notes': kwargs.get('notes', ''),
                        'notify_on_stock': kwargs.get('notify_on_stock', True),
                        'notify_on_discount': kwargs.get('notify_on_discount', True),
                        'notify_price_drop': kwargs.get('notify_price_drop', True),
                    }
                )
                
                if created:
                    # Item was added
                    wishlist_count = models.Wishlist.objects.filter(user=user).count()
                    
                    return ToggleWishlist(
                        success=True,
                        message=f"Added '{product.name_ar}' to wishlist",
                        is_in_wishlist=True,
                        wishlist_item=wishlist_item,
                        wishlist_count=wishlist_count
                    )
                else:
                    # Item was removed
                    wishlist_item.delete()
                    wishlist_count = models.Wishlist.objects.filter(user=user).count()
                    
                    return ToggleWishlist(
                        success=True,
                        message=f"Removed '{product.name_ar}' from wishlist",
                        is_in_wishlist=False,
                        wishlist_item=None,
                        wishlist_count=wishlist_count
                    )
                    
        except models.Product.DoesNotExist:
            return ToggleWishlist(
                success=False, 
                message="Product not found",
                is_in_wishlist=False
            )
        except Exception as e:
            return ToggleWishlist(
                success=False, 
                message=str(e),
                is_in_wishlist=False
            )


class ClearWishlist(Mutation):
    """Clear all items from user's wishlist"""
    
    success = Boolean()
    message = String()
    cleared_count = Field(Int)

    def mutate(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return ClearWishlist(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                wishlist_items = models.Wishlist.objects.filter(user=user)
                cleared_count = wishlist_items.count()
                wishlist_items.delete()
                
                return ClearWishlist(
                    success=True,
                    message=f"Cleared {cleared_count} items from wishlist",
                    cleared_count=cleared_count
                )
                
        except Exception as e:
            return ClearWishlist(
                success=False, 
                message=str(e)
            )


class MoveToCart(Mutation):
    """Move wishlist item to cart"""
    
    class Arguments:
        wishlist_item_id = Int(required=True)
        quantity = Int(default_value=1)
        material_id = Int()
        width = Float()
        height = Float()
        dimension_unit = String(default_value='cm')
        delivery_type = String(default_value='home')
        wilaya_id = String()

    success = Boolean()
    message = String()
    cart_item = Field(CartItemNode)
    removed_from_wishlist = Field(Boolean)

    def mutate(self, info, wishlist_item_id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return MoveToCart(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                wishlist_item = models.Wishlist.objects.get(
                    id=wishlist_item_id,
                    user=user
                )
                
                # Add to cart using existing cart logic
                # Check if cart item already exists
                cart_item, created = models.CartItem.objects.get_or_create(
                    user=user,
                    product=wishlist_item.product,
                    material_id=kwargs.get('material_id'),
                    width=kwargs.get('width'),
                    height=kwargs.get('height'),
                    defaults={
                        'quantity': kwargs.get('quantity', 1),
                        'dimension_unit': kwargs.get('dimension_unit', 'cm'),
                        'delivery_type': kwargs.get('delivery_type', 'home'),
                        'unit_price': wishlist_item.product.base_price,
                        'material_price': 0,  # Calculate if material provided
                    }
                )
                
                if not created:
                    # Update existing cart item quantity
                    cart_item.quantity += kwargs.get('quantity', 1)
                    cart_item.save()
                
                # Remove from wishlist
                wishlist_item.delete()
                
                return MoveToCart(
                    success=True,
                    message=f"Moved '{wishlist_item.product.name_ar}' to cart",
                    cart_item=cart_item,
                    removed_from_wishlist=True
                )
                
        except models.Wishlist.DoesNotExist:
            return MoveToCart(
                success=False, 
                message="Wishlist item not found"
            )
        except Exception as e:
            return MoveToCart(
                success=False, 
                message=str(e)
            )

                        class CreateReview(Mutation):
    class Arguments:
        input = ReviewInput(required=True)

    review = Field(ReviewNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateReview(success=False, message="Authentication required")
        
        try:
            product = models.Product.objects.get(id=input.product_id)
            
            # Check if user already reviewed this product
            if models.Review.objects.filter(user=info.context.user, product=product).exists():
                return CreateReview(success=False, message="You have already reviewed this product")
            
            review = models.Review.objects.create(
                user=info.context.user,
                product=product,
                rating=input.rating,
                comment=input.comment
            )
            
            return CreateReview(review=review, success=True, message="Review created successfully")
        except Exception as e:
            return CreateReview(success=False, message=str(e))


# Authentication Mutations
class Login(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    success = Boolean()
    message = String()
    token = String()
    refreshToken = String()
    user = Field(UserNode)

    def mutate(self, info, username, password):
        from django.contrib.auth import authenticate
        from django.contrib.auth import login as django_login
        import jwt
        from datetime import datetime, timedelta
        from django.conf import settings
        
        try:
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # Generate JWT tokens
                    payload = {
                        'user_id': user.id,
                        'username': user.username,
                        'exp': datetime.utcnow() + timedelta(hours=24),
                        'iat': datetime.utcnow()
                    }
                    
                    refresh_payload = {
                        'user_id': user.id,
                        'exp': datetime.utcnow() + timedelta(days=7),
                        'iat': datetime.utcnow()
                    }
                    
                    # Simple token generation (in production, use proper JWT library)
                    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
                    
                    return Login(
                        success=True,
                        message="Login successful",
                        token=token,
                        refreshToken=refresh_token,
                        user=user
                    )
                else:
                    return Login(success=False, message="Account is disabled")
            else:
                return Login(success=False, message="Invalid credentials")
        except Exception as e:
            return Login(success=False, message=str(e))


class Register(Mutation):
    class Arguments:
        username = String(required=True)
        email = String(required=True)
        password = String(required=True)
        firstName = String(required=True)
        lastName = String(required=True)

    success = Boolean()
    message = String()
    user = Field(UserNode)

    def mutate(self, info, username, email, password, firstName, lastName):
        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return Register(success=False, message="Username already exists")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return Register(success=False, message="Email already exists")
            
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstName,
                last_name=lastName
            )
            
            # Create user profile
            models.UserProfile.objects.create(
                user=user,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return Register(
                success=True,
                message="Registration successful",
                user=user
            )
        except Exception as e:
            return Register(success=False, message=str(e))


class UpdateProfile(Mutation):
    class Arguments:
        firstName = String()
        lastName = String()
        phone = String()
        address = String()
        bio = String()
        wilayaId = ID()

    success = Boolean()
    message = String()
    user = Field(UserNode)

    def mutate(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            return UpdateProfile(success=False, message="Authentication required")
        
        try:
            user = info.context.user
            
            # Update user fields
            if 'firstName' in kwargs:
                user.first_name = kwargs['firstName']
            if 'lastName' in kwargs:
                user.last_name = kwargs['lastName']
            
            user.save()
            
            # Update or create profile
            profile, created = models.UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
            
            if 'phone' in kwargs:
                profile.phone = kwargs['phone']
            if 'address' in kwargs:
                profile.address = kwargs['address']
            if 'bio' in kwargs:
                profile.bio = kwargs['bio']
            if 'wilayaId' in kwargs:
                try:
                    wilaya = models.Shipping.objects.get(wilaya_id=kwargs['wilayaId'])
                    # Note: You might need to add a foreign key field to UserProfile for wilaya
                except models.Shipping.DoesNotExist:
                    pass
            
            profile.updated_at = datetime.utcnow()
            profile.save()
            
            return UpdateProfile(
                success=True,
                message="Profile updated successfully",
                user=user
            )
        except Exception as e:
            return UpdateProfile(success=False, message=str(e))


class Mutation(ObjectType, OrganizationMutation):
    # Authentication mutations
    login = Login.Field()
    register = Register.Field()
    updateProfile = UpdateProfile.Field()
    
    # Product mutations (Staff only)
    create_category = CreateCategory.Field()
    create_product = CreateProduct.Field()
    
    # Order and Payment mutations (Financial operations)
    create_order = CreateOrder.Field()
    process_payment = ProcessPayment.Field()
    
    # User interactions
    add_to_cart = AddToCart.Field()
    update_cart_quantity = UpdateCartQuantity.Field()
    remove_from_cart = RemoveFromCart.Field()
    apply_coupon = ApplyCoupon.Field()
    set_shipping = SetShipping.Field()
    add_to_wishlist = AddToWishlist.Field()
    create_review = CreateReview.Field()


# Enhanced Query with Vinyls and Investors focus
class Query(ObjectType, OrganizationQuery):
    hello = String(name=String(default_value="World"))

    # Node interface for relay
    node = relay.Node.Field()

    # User related
    me = Field(UserNode)
    my_profile = Field(UserProfileNode)
    my_orders = List(OrderNode)
    my_cart = List(CartItemNode)
    my_wishlist = List(WishlistNode)

    # Products (Vinyls) - Main focus
    products = DjangoFilterConnectionField(ProductNode)
    product = relay.Node.Field(ProductNode)
    featured_products = List(ProductNode)
    new_products = List(ProductNode)
    sale_products = List(ProductNode)
    search_products = List(ProductNode, query=String())

    # Categories and Materials
    categories = DjangoFilterConnectionField(CategoryNode)
    materials = DjangoFilterConnectionField(MaterialNode)

    # Orders (Financial operations)
    orders = DjangoFilterConnectionField(OrderNode)
    order = relay.Node.Field(OrderNode)
    order_by_number = Field(OrderNode, order_number=String())

    # Users (Investors) - Staff only
    users = List(UserNode)
    user = relay.Node.Field(UserNode)
    investors = List(UserNode)  # Alias for users with specific permissions

    # Organization
    organization = Field(OrganizationObjectType)
    organizations = List(OrganizationObjectType)
    social_links = List(OrganizationObjectType, organization_id=ID())
    social_links_by_type = List(OrganizationObjectType, organization_id=ID(), platform_type=String())

    # Other entities
    shipping_options = DjangoFilterConnectionField(ShippingNode)
    reviews = DjangoFilterConnectionField(ReviewNode)
    designs = DjangoFilterConnectionField(DesignNode)
    blog_posts = DjangoFilterConnectionField(BlogPostNode)
    notifications = DjangoFilterConnectionField(NotificationNode)
    
    # Categories and Materials (Expanded)
    category = relay.Node.Field(CategoryNode)
    material = relay.Node.Field(MaterialNode)
    categoryTree = List(CategoryNode)
    rootCategories = List(CategoryNode)
    categoryBySlug = Field(CategoryNode, slug=String())
    
    # Orders and Payments (Expanded)
    payment = relay.Node.Field(PaymentNode)
    order_timeline = List(OrderTimelineNode, orderId=ID())
    
    # Cart and Wishlist (Expanded)
    cart_item = relay.Node.Field(CartItemNode)
    wishlist_item = relay.Node.Field(WishlistNode)
    
    # Reviews and Reports
    review = relay.Node.Field(ReviewNode)
    review_reports = List(ReviewReportNode, reviewId=ID())
    
    # Designs and Categories
    design = relay.Node.Field(DesignNode)
    design_category = relay.Node.Field(DesignCategoryNode)
    design_categories = DjangoFilterConnectionField(DesignCategoryNode)
    
    # Blog and Content
    blog_post = relay.Node.Field(BlogPostNode)
    blog_category = relay.Node.Field(BlogCategoryNode)
    blog_categories = DjangoFilterConnectionField(BlogCategoryNode)
    
    # Notifications and Alerts
    notification = relay.Node.Field(NotificationNode)
    alerts = DjangoFilterConnectionField(AlertNode)
    alert = relay.Node.Field(AlertNode)
    
    # System and Analytics
    erp_sync_logs = DjangoFilterConnectionField(ERPNextSyncLogNode)
    behavior_tracking = DjangoFilterConnectionField(BehaviorTrackingNode)
    forecasts = DjangoFilterConnectionField(ForecastNode)
    customer_segments = List(CustomerSegmentNode)
    pricing_engine = Field(PricingEngineNode)
    
    # Conversations and AI
    conversation_history = List(ConversationHistoryNode, sessionId=String())
    
    # Dashboard and Settings
    dashboard_settings = Field(DashboardSettingsNode)
    wishlist_settings = Field(WishlistSettingsNode)
    
    # Coupons and Discounts
    coupons = DjangoFilterConnectionField(CouponNode)
    coupon = relay.Node.Field(CouponNode)
    validate_coupon = Field(CouponNode, code=String())

    def resolve_hello(self, info, name):
        return f'Hello {name}!'

    def resolve_me(self, info):
        if info.context.user.is_authenticated:
            return info.context.user
        return None

    def resolve_my_profile(self, info):
        if info.context.user.is_authenticated:
            try:
                return info.context.user.profile
            except models.UserProfile.DoesNotExist:
                return None
        return None

    def resolve_my_orders(self, info):
        if info.context.user.is_authenticated:
            return models.Order.objects.filter(user=info.context.user)
        return []

    def resolve_my_cart(self, info):
        if info.context.user.is_authenticated:
            return models.CartItem.objects.filter(user=info.context.user)
        return []

    def resolve_my_wishlist(self, info):
        if info.context.user.is_authenticated:
            return models.Wishlist.objects.filter(user=info.context.user)
        return []

    def resolve_products(self, info, **kwargs):
        return models.Product.objects.filter(is_active=True)

    def resolve_featured_products(self, info):
        return models.Product.objects.filter(is_featured=True, is_active=True)[:10]

    def resolve_new_products(self, info):
        return models.Product.objects.filter(is_new=True, is_active=True)[:10]

    def resolve_sale_products(self, info):
        return models.Product.objects.filter(on_sale=True, is_active=True)[:10]

    def resolve_search_products(self, info, query=None):
        if not query:
            return models.Product.objects.none()
        
        return models.Product.objects.filter(
            is_active=True
        ).filter(
            models.Q(name_ar__icontains=query) |
            models.Q(name_en__icontains=query) |
            models.Q(description_ar__icontains=query) |
            models.Q(description_en__icontains=query) |
            models.Q(tags__contains=[query])
        )

    def resolve_orders(self, info, **kwargs):
        if info.context.user.is_authenticated:
            if info.context.user.is_staff:
                return models.Order.objects.all()
            else:
                return models.Order.objects.filter(user=info.context.user)
        return models.Order.objects.none()

    def resolve_order_by_number(self, info, order_number):
        if info.context.user.is_authenticated:
            try:
                order = models.Order.objects.get(order_number=order_number)
                # Check permissions
                if order.user == info.context.user or info.context.user.is_staff:
                    return order
            except models.Order.DoesNotExist:
                return None
        return None

    def resolve_users(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return User.objects.filter(is_active=True)
        return []

    def resolve_investors(self, info):
        """Query for investors - users with specific permissions or groups"""
        if info.context.user.is_authenticated and info.context.user.is_staff:
            # You can customize this logic based on your investor definition
            # For example, users in 'investors' group or with specific permissions
            return User.objects.filter(
                is_active=True,
                groups__name__in=['investors']  # Assuming you have an 'investors' group
            ).distinct()
        return []
    
    def resolve_category(self, info, id=None, slug=None):
        if id:
            try:
                return models.Category.objects.get(id=id, is_active=True)
            except models.Category.DoesNotExist:
                return None
        elif slug:
            try:
                return models.Category.objects.get(slug=slug, is_active=True)
            except models.Category.DoesNotExist:
                return None
        return None
    
    def resolve_categoryTree(self, info):
        """Return hierarchical category tree structure"""
        categories = models.Category.objects.filter(is_active=True).order_by('name_ar')
        
        def build_tree(parent=None):
            children = []
            for category in categories:
                if category.parent_id == (parent.id if parent else None):
                    category_node = {
                        'id': category.id,
                        'name_ar': category.name_ar,
                        'name_en': category.name_en,
                        'slug': category.slug,
                        'icon': category.icon,
                        'image': category.image,
                        'description': category.description,
                        'waste_percent': category.waste_percent,
                        'is_active': category.is_active,
                        'level': 0,
                        'children': build_tree(category),
                        'created_at': category.created_at,
                        'updated_at': category.updated_at,
                    }
                    children.append(category_node)
            return children
        
        return build_tree()
    
    def resolve_rootCategories(self, info):
        """Return top-level categories (without parent)"""
        return models.Category.objects.filter(parent=None, is_active=True).order_by('name_ar')
    
    def resolve_categoryBySlug(self, info, slug):
        """Get category by slug"""
        try:
            return models.Category.objects.get(slug=slug, is_active=True)
        except models.Category.DoesNotExist:
            return None
    
    def resolve_material(self, info, id):
        try:
            return models.Material.objects.get(id=id, is_active=True)
        except models.Material.DoesNotExist:
            return None
    
    def resolve_payment(self, info, id):
        if info.context.user.is_authenticated:
            try:
                payment = models.Payment.objects.get(id=id)
                # Check permissions
                if (payment.order.user == info.context.user or 
                    info.context.user.is_staff):
                    return payment
            except models.Payment.DoesNotExist:
                return None
        return None
    
    def resolve_order_timeline(self, info, orderId):
        if info.context.user.is_authenticated:
            try:
                order = models.Order.objects.get(id=orderId)
                if (order.user == info.context.user or 
                    info.context.user.is_staff):
                    return models.OrderTimeline.objects.filter(order=order)
            except models.Order.DoesNotExist:
                return []
        return []
    
    def resolve_cart_item(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.CartItem.objects.get(id=id, user=info.context.user)
            except models.CartItem.DoesNotExist:
                return None
        return None
    
    def resolve_wishlist_item(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.Wishlist.objects.get(id=id, user=info.context.user)
            except models.Wishlist.DoesNotExist:
                return None
        return None
    
    def resolve_review(self, info, id):
        try:
            return models.Review.objects.get(id=id, is_verified=True)
        except models.Review.DoesNotExist:
            return None
    
    def resolve_review_reports(self, info, reviewId):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.ReviewReport.objects.filter(review_id=reviewId)
        return []
    
    def resolve_design(self, info, id):
        try:
            return models.Design.objects.get(id=id, is_active=True)
        except models.Design.DoesNotExist:
            return None
    
    def resolve_design_category(self, info, id):
        try:
            return models.DesignCategory.objects.get(id=id, is_active=True)
        except models.DesignCategory.DoesNotExist:
            return None
    
    def resolve_blog_post(self, info, id=None, slug=None):
        try:
            if id:
                return models.BlogPost.objects.get(id=id, is_published=True)
            elif slug:
                return models.BlogPost.objects.get(slug=slug, is_published=True)
        except models.BlogPost.DoesNotExist:
            return None
        return None
    
    def resolve_blog_category(self, info, id):
        try:
            return models.BlogCategory.objects.get(id=id)
        except models.BlogCategory.DoesNotExist:
            return None
    
    def resolve_notification(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.Notification.objects.get(id=id, user=info.context.user)
            except models.Notification.DoesNotExist:
                return None
        return None
    
    def resolve_alerts(self, info, **kwargs):
        if info.context.user.is_authenticated:
            return models.Alert.objects.filter(user=info.context.user, is_active=True)
        return models.Alert.objects.none()
    
    def resolve_alert(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.Alert.objects.get(id=id, user=info.context.user)
            except models.Alert.DoesNotExist:
                return None
        return None
    
    def resolve_erp_sync_logs(self, info, **kwargs):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.ERPNextSyncLog.objects.all()
        return models.ERPNextSyncLog.objects.none()
    
    def resolve_behavior_tracking(self, info, **kwargs):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.BehaviorTracking.objects.all()
        return models.BehaviorTracking.objects.none()
    
    def resolve_forecasts(self, info, **kwargs):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.Forecast.objects.all()
        return models.Forecast.objects.none()
    
    def resolve_customer_segments(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.CustomerSegment.objects.all()
        return []
    
    def resolve_pricing_engine(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            try:
                return models.PricingEngine.objects.first()
            except models.PricingEngine.DoesNotExist:
                return None
        return None
    
    def resolve_conversation_history(self, info, sessionId=None):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            if sessionId:
                return models.ConversationHistory.objects.filter(session_id=sessionId)
            return models.ConversationHistory.objects.all()
        return []
    
    def resolve_dashboard_settings(self, info):
        if info.context.user.is_authenticated:
            try:
                return info.context.user.dashboard_settings
            except models.DashboardSettings.DoesNotExist:
                return None
        return None
    
    def resolve_wishlist_settings(self, info):
        if info.context.user.is_authenticated:
            try:
                return info.context.user.wishlist_settings
            except models.WishlistSettings.DoesNotExist:
                return None
        return None
    
    def resolve_validate_coupon(self, info, code):
        try:
            coupon = models.Coupon.objects.get(code=code.upper(), is_active=True)
            # Add validation logic here (check dates, usage limits, etc.)
            return coupon
        except models.Coupon.DoesNotExist:
            return None


# Combine all queries and mutations
class Query(APIQuery):
    """Root query combining all domain queries"""
    pass

class Mutation(APIMutation):
    """Root mutation combining all domain mutations"""
    pass

# Export schema
schema = Schema(query=Query, mutation=Mutation)
