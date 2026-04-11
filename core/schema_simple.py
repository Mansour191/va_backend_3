"""
Simplified GraphQL Schema for VynilArt
"""
from graphene import relay, ObjectType, Schema, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from api import models

User = get_user_model()


# Basic Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')


class ProductType(DjangoObjectType):
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
        }


class CategoryType(DjangoObjectType):
    class Meta:
        model = models.Category
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
        }


class OrderType(DjangoObjectType):
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


class CartItemType(DjangoObjectType):
    class Meta:
        model = models.CartItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
        }


class WishlistType(DjangoObjectType):
    class Meta:
        model = models.Wishlist
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
        }


class ReviewType(DjangoObjectType):
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


# Input Types
class ProductInput(graphene.InputObjectType):
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String(required=True)
    description_ar = String()
    description_en = String()
    base_price = Float(required=True)
    category_id = Int()
    is_featured = Boolean()
    is_new = Boolean()
    is_active = Boolean()


class OrderInput(graphene.InputObjectType):
    customer_name = String(required=True)
    phone = String(required=True)
    email = String()
    shipping_address = String(required=True)
    payment_method = String()
    notes = String()


class CartItemInput(graphene.InputObjectType):
    product_id = Int(required=True)
    quantity = Int(default_value=1)


class ReviewInput(graphene.InputObjectType):
    product_id = Int(required=True)
    rating = Int(required=True)
    comment = String()


# Mutations
class CreateProduct(Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = Field(ProductType)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateProduct(success=False, message="Staff privileges required")
        
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
                category=category,
                is_featured=input.is_featured or False,
                is_new=input.is_new or True,
                is_active=input.is_active or True
            )
            
            return CreateProduct(product=product, success=True, message="Product created successfully")
        except Exception as e:
            return CreateProduct(success=False, message=str(e))


class CreateOrder(Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = Field(OrderType)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateOrder(success=False, message="Authentication required")
        
        try:
            import uuid
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            order = models.Order.objects.create(
                order_number=order_number,
                user=info.context.user,
                customer_name=input.customer_name,
                phone=input.phone,
                email=input.email,
                shipping_address=input.shipping_address,
                payment_method=input.payment_method or 'cod',
                notes=input.notes,
                total_amount=0,  # Will be calculated
                subtotal=0,
                tax=0,
                shipping_cost=0
            )
            
            return CreateOrder(order=order, success=True, message="Order created successfully")
        except Exception as e:
            return CreateOrder(success=False, message=str(e))


class AddToCart(Mutation):
    class Arguments:
        input = CartItemInput(required=True)

    cart_item = Field(CartItemType)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return AddToCart(success=False, message="Authentication required")
        
        try:
            product = models.Product.objects.get(id=input.product_id)
            
            cart_item, created = models.CartItem.objects.get_or_create(
                user=info.context.user,
                product=product,
                defaults={'quantity': input.quantity}
            )
            
            if not created:
                cart_item.quantity += input.quantity
                cart_item.save()
            
            return AddToCart(cart_item=cart_item, success=True, message="Added to cart")
        except Exception as e:
            return AddToCart(success=False, message=str(e))


class CreateReview(Mutation):
    class Arguments:
        input = ReviewInput(required=True)

    review = Field(ReviewType)
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


# Query Class
class Query(ObjectType):
    hello = String(name=String(default_value="World"))
    
    # Products
    products = DjangoFilterConnectionField(ProductType)
    product = Field(ProductType, id=ID(), slug=String())
    featured_products = List(ProductType)
    new_products = List(ProductType)
    sale_products = List(ProductType)
    
    # Categories
    categories = DjangoFilterConnectionField(CategoryType)
    
    # Orders
    orders = DjangoFilterConnectionField(OrderType)
    my_orders = List(OrderType)
    
    # Cart and Wishlist
    my_cart = List(CartItemType)
    my_wishlist = List(WishlistType)
    
    # Reviews
    reviews = DjangoFilterConnectionField(ReviewType)
    
    # Users
    users = List(UserType)
    me = Field(UserType)
    
    def resolve_hello(self, info, name):
        return f'Hello {name}!'
    
    def resolve_me(self, info):
        if info.context.user.is_authenticated:
            return info.context.user
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
    
    def resolve_users(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return User.objects.filter(is_active=True)
        return []


# Mutation Class
class Mutation(ObjectType):
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    add_to_cart = AddToCart.Field()
    create_review = CreateReview.Field()


# Schema Definition
schema = Schema(query=Query, mutation=Mutation)
