"""
Enhanced Cart Schema for VynilArt API
"""
import graphene
import json
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from api.models.cart import CartItem
from api.models.product import Product, Material
from api.models.shipping import Shipping

User = get_user_model()


class CartItemType(DjangoObjectType):
    """Enhanced Cart Item type with all required fields"""
    
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
    
    # Additional fields for better integration
    weight = Field(Float)
    dimensions = Field(String)
    
    class Meta:
        model = CartItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
            'material': ['exact'],
        }

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
    
    def resolve_subtotal(self, info):
        """Calculate subtotal for this cart item"""
        # Simple subtotal calculation based on product base price and quantity
        unit_price = float(self.product.base_price)
        material_price = 0
        if self.material and self.options:
            # Calculate material price from options if width/height provided
            width = self.options.get('width')
            height = self.options.get('height')
            if width and height:
                area_m2 = (float(width) * float(height)) / 10000
                material_price = float(self.material.price_per_m2 * area_m2)
        return (unit_price + material_price) * self.quantity
    
    def resolve_total_with_discount(self, info):
        """Calculate total after discount (no discount for now)"""
        return self.resolve_subtotal(info)
    
    def resolve_final_total(self, info):
        """Calculate final total including shipping (no shipping for now)"""
        return self.resolve_subtotal(info)
    
    def resolve_is_available(self, info):
        """Check if product is available"""
        return self.product.is_active and self.product.stock > 0
    
    def resolve_max_quantity(self, info):
        """Get maximum quantity available"""
        return self.product.stock
    
    def resolve_current_unit_price(self, info):
        """Get current unit price from product"""
        return float(self.product.base_price)
    
    def resolve_current_material_price(self, info):
        """Get current material price"""
        if self.material and self.options:
            width = self.options.get('width')
            height = self.options.get('height')
            if width and height:
                area_m2 = (float(width) * float(height)) / 10000
                return float(self.material.price_per_m2 * area_m2)
            return float(self.material.price_per_m2)
        return 0.0
    
    def resolve_price_changed(self, info):
        """Check if price has changed since cart item was created (simplified)"""
        # For now, always return False as we don't store historical prices
        return False
    
    def resolve_weight(self, info):
        """Get total weight for this cart item"""
        product_weight = float(self.product.weight) if self.product.weight else 0
        return product_weight * self.quantity
    
    def resolve_dimensions(self, info):
        """Get formatted dimensions from options"""
        if self.options:
            width = self.options.get('width')
            height = self.options.get('height')
            dimension_unit = self.options.get('dimension_unit', 'cm')
            if width and height:
                return f"{width}×{height} {dimension_unit}"
        return None


# Input Types
class CartItemInput(graphene.InputObjectType):
    """Input for cart item operations matching SQL schema"""
    product_id = Int(required=True)
    material_id = Int()
    quantity = Int(default_value=1)
    options = JSONString()


class UpdateCartInput(graphene.InputObjectType):
    """Input for updating cart quantity"""
    cart_item_id = Int(required=True)
    quantity = Int(required=True)


# Cart Mutations
class AddToCart(Mutation):
    """Add to cart mutation matching SQL schema"""
    
    class Arguments:
        input = CartItemInput(required=True)

    cart_item = Field(CartItemType)
    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return AddToCart(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=input.product_id)
                
                # Stock validation
                if not product.is_active:
                    return AddToCart(
                        success=False, 
                        message="Product is not available"
                    )
                
                if product.stock < input.quantity:
                    return AddToCart(
                        success=False, 
                        message=f"Only {product.stock} items available"
                    )
                
                material = None
                if input.material_id:
                    material = Material.objects.get(id=input.material_id)
                
                # Parse options
                options = {}
                if input.options:
                    options = json.loads(input.options) if isinstance(input.options, str) else input.options
                
                # Get or create cart item
                cart_item, created = CartItem.objects.get_or_create(
                    user=user,
                    product=product,
                    material=material,
                    defaults={
                        'quantity': input.quantity,
                        'options': options,
                    }
                )
                
                if not created:
                    # Update existing item
                    new_quantity = cart_item.quantity + input.quantity
                    if new_quantity > product.stock:
                        return AddToCart(
                            success=False, 
                            message=f"Only {product.stock} items available in total"
                        )
                    
                    cart_item.quantity = new_quantity
                    # Update options if provided
                    if options:
                        cart_item.options.update(options)
                    cart_item.save()
                
                # Get cart summary
                cart_items = CartItem.objects.filter(user=user).select_related('product', 'material')
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.product.base_price) * item.quantity for item in cart_items),
                }
                
                return AddToCart(
                    cart_item=cart_item,
                    success=True,
                    message="Added to cart successfully",
                    cart_summary=json.dumps(cart_summary)
                )
                
        except Product.DoesNotExist:
            return AddToCart(success=False, message="Product not found")
        except Material.DoesNotExist:
            return AddToCart(success=False, message="Material not found")
        except Exception as e:
            return AddToCart(success=False, message=str(e))


class UpdateCartQuantity(Mutation):
    """Update cart quantity mutation"""
    
    class Arguments:
        input = UpdateCartInput(required=True)

    cart_item = Field(CartItemType)
    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateCartQuantity(success=False, message="Authentication required")
        
        try:
            with transaction.atomic():
                cart_item = CartItem.objects.select_for_update().get(
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
                    cart_item = None
                else:
                    cart_item.quantity = input.quantity
                    cart_item.save()
                    message = "Cart updated successfully"
                
                # Get updated cart summary
                cart_items = CartItem.objects.filter(user=user).select_related('product', 'material')
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.product.base_price) * item.quantity for item in cart_items),
                }
                
                return UpdateCartQuantity(
                    cart_item=cart_item,
                    success=True,
                    message=message,
                    cart_summary=json.dumps(cart_summary)
                )
                
        except CartItem.DoesNotExist:
            return UpdateCartQuantity(success=False, message="Cart item not found")
        except Exception as e:
            return UpdateCartQuantity(success=False, message=str(e))


class RemoveFromCart(Mutation):
    """Remove from cart mutation"""
    
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
            with transaction.atomic():
                cart_item = CartItem.objects.get(
                    id=cart_item_id,
                    user=user
                )
                cart_item.delete()
                
                # Get updated cart summary
                cart_items = CartItem.objects.filter(user=user).select_related('product', 'material')
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.product.base_price) * item.quantity for item in cart_items),
                }
                
                return RemoveFromCart(
                    success=True,
                    message="Item removed from cart",
                    cart_summary=json.dumps(cart_summary)
                )
                
        except CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Cart item not found")
        except Exception as e:
            return RemoveFromCart(success=False, message=str(e))


# Query Class
class CartQuery(ObjectType):
    """Cart queries"""
    
    my_cart = List(CartItemType)
    cart_item = Field(CartItemType, id=ID(required=True))
    cart_summary = Field(JSONString)
    
    def resolve_my_cart(self, info):
        """Get current user's cart"""
        if not info.context.user.is_authenticated:
            return []
        
        return CartItem.objects.filter(user=info.context.user).select_related('product', 'material')
    
    def resolve_cart_item(self, info, id):
        """Get specific cart item"""
        if not info.context.user.is_authenticated:
            return None
        
        try:
            return CartItem.objects.get(
                id=id,
                user=info.context.user
            )
        except CartItem.DoesNotExist:
            return None
    
    def resolve_cart_summary(self, info):
        """Get cart summary"""
        if not info.context.user.is_authenticated:
            return json.dumps({})
        
        cart_items = CartItem.objects.filter(user=info.context.user).select_related('product', 'material')
        
        summary = {
            'total_items': cart_items.count(),
            'subtotal': sum(float(item.product.base_price) * item.quantity for item in cart_items),
            'available_items': sum(1 for item in cart_items if item.product.is_active and item.product.stock > 0),
            'unavailable_items': sum(1 for item in cart_items if not (item.product.is_active and item.product.stock > 0)),
        }
        
        return json.dumps(summary)


# Mutation Class
class CartMutation(ObjectType):
    """Cart mutations"""
    
    add_to_cart = AddToCart.Field()
    update_cart_quantity = UpdateCartQuantity.Field()
    remove_from_cart = RemoveFromCart.Field()
