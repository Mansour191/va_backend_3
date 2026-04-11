"""
Enhanced Wishlist Schema for VynilArt API
"""
import graphene
import json
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, F
from api.models.wishlist import Wishlist, WishlistSettings
from api.models.product import Product

User = get_user_model()


class WishlistType(DjangoObjectType):
    """Enhanced Wishlist type with all required fields"""
    
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
    price_dropped = Field(Boolean)
    
    # Additional fields for better integration
    days_in_wishlist = Field(Int)
    
    class Meta:
        model = Wishlist
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
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
        if self.product.on_sale and self.product.discount_percent > 0:
            return float(self.product.base_price * (1 - self.product.discount_percent / 100))
        return float(self.product.base_price)
    
    def resolve_has_discount(self, info):
        """Check if product has discount"""
        return self.product.on_sale and self.product.discount_percent > 0
    
    def resolve_discount_percentage(self, info):
        """Get discount percentage"""
        return self.product.discount_percent if self.product.on_sale else 0
    
    def resolve_discounted_price(self, info):
        """Calculate discounted price"""
        if self.product.on_sale and self.product.discount_percent > 0:
            return float(self.product.base_price * (1 - self.product.discount_percent / 100))
        return float(self.product.base_price)
    
    def resolve_savings_amount(self, info):
        """Calculate savings amount"""
        if self.product.on_sale and self.product.discount_percent > 0:
            return float(self.product.base_price * self.product.discount_percent / 100)
        return 0.0
    
    def resolve_price_dropped(self, info):
        """Check if price dropped"""
        # This would require price history tracking - for now return False
        return False
    
    def resolve_days_in_wishlist(self, info):
        """Calculate days since added to wishlist"""
        if self.created_at:
            return (timezone.now() - self.created_at).days
        return 0


class WishlistSettingsType(DjangoObjectType):
    """Wishlist settings type"""
    
    class Meta:
        model = WishlistSettings
        interfaces = (relay.Node,)
        fields = '__all__'


# Input Types
class WishlistItemInput(graphene.InputObjectType):
    """Input for adding item to wishlist"""
    product_id = Int(required=True)
    priority = Int(default_value=0)
    notes = String()
    notify_on_stock = Boolean(default_value=True)
    notify_on_discount = Boolean(default_value=True)
    notify_price_drop = Boolean(default_value=True)


class WishlistSettingsInput(graphene.InputObjectType):
    """Input for updating wishlist settings"""
    items_per_page = Int()
    sort_by = String()
    sort_order = String()
    email_notifications = Boolean()
    push_notifications = Boolean()
    auto_remove_out_of_stock = Boolean()
    auto_remove_discontinued = Boolean()
    make_public = Boolean()


# Enhanced Mutations
class ToggleWishlist(Mutation):
    """Toggle item in wishlist (add if not exists, remove if exists)"""
    
    class Arguments:
        input = WishlistItemInput(required=True)

    success = Boolean()
    message = String()
    is_in_wishlist = Field(Boolean)
    wishlist_item = Field(WishlistType)
    wishlist_count = Field(Int)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return ToggleWishlist(
                success=False, 
                message="Authentication required",
                is_in_wishlist=False
            )
        
        try:
            with transaction.atomic():
                product = Product.objects.get(id=input.product_id)
                
                # Check if item already exists
                wishlist_item, created = Wishlist.objects.get_or_create(
                    user=user,
                    product=product
                )
                
                if created:
                    # Item was added
                    wishlist_count = Wishlist.objects.filter(user=user).count()
                    
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
                    wishlist_count = Wishlist.objects.filter(user=user).count()
                    
                    return ToggleWishlist(
                        success=True,
                        message=f"Removed '{product.name_ar}' from wishlist",
                        is_in_wishlist=False,
                        wishlist_item=None,
                        wishlist_count=wishlist_count
                    )
                    
        except Product.DoesNotExist:
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
                wishlist_items = Wishlist.objects.filter(user=user)
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


class UpdateWishlistItem(Mutation):
    """Update wishlist item settings"""
    
    class Arguments:
        wishlist_item_id = ID(required=True)
        priority = Int()
        notes = String()
        notify_on_stock = Boolean()
        notify_on_discount = Boolean()
        notify_price_drop = Boolean()

    success = Boolean()
    message = String()
    wishlist_item = Field(WishlistType)

    def mutate(self, info, wishlist_item_id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateWishlistItem(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                wishlist_item = Wishlist.objects.get(
                    id=wishlist_item_id,
                    user=user
                )
                
                # Update fields (only those that exist in the model)
                for field, value in kwargs.items():
                    if value is not None and hasattr(wishlist_item, field):
                        setattr(wishlist_item, field, value)
                
                wishlist_item.save()
                
                return UpdateWishlistItem(
                    success=True,
                    message="Wishlist item updated successfully",
                    wishlist_item=wishlist_item
                )
                
        except models.Wishlist.DoesNotExist:
            return UpdateWishlistItem(
                success=False, 
                message="Wishlist item not found"
            )
        except Exception as e:
            return UpdateWishlistItem(
                success=False, 
                message=str(e)
            )


class MoveToCart(Mutation):
    """Move wishlist item to cart"""
    
    class Arguments:
        wishlist_item_id = ID(required=True)
        quantity = Int(default_value=1)
        material_id = Int()
        width = Float()
        height = Float()
        dimension_unit = String(default_value='cm')
        delivery_type = String(default_value='home')
        wilaya_id = String()

    success = Boolean()
    message = String()
    cart_item = Field('api.schema.cart_schema.CartItemType')
    removed_from_wishlist = Field(Boolean)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return MoveToCart(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                wishlist_item = Wishlist.objects.get(
                    id=kwargs['wishlist_item_id'],
                    user=user
                )
                
                # Add to cart using existing cart logic
                from api.models.cart import CartItem
                
                # Check if cart item already exists
                cart_item, created = CartItem.objects.get_or_create(
                    user=user,
                    product=wishlist_item.product,
                    material_id=kwargs.get('material_id'),
                    defaults={
                        'quantity': kwargs.get('quantity', 1),
                        'options': {
                            'width': kwargs.get('width'),
                            'height': kwargs.get('height'),
                            'dimension_unit': kwargs.get('dimension_unit', 'cm'),
                            'delivery_type': kwargs.get('delivery_type', 'home')
                        }
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


class UpdateWishlistSettings(Mutation):
    """Update user wishlist settings"""
    
    class Arguments:
        input = WishlistSettingsInput(required=True)

    success = Boolean()
    message = String()
    settings = Field(WishlistSettingsType)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateWishlistSettings(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                settings, created = WishlistSettings.objects.get_or_create(
                    user=user,
                    defaults={
                        'items_per_page': 20,
                        'sort_by': 'created_at',
                        'sort_order': 'desc',
                        'email_notifications': True,
                        'push_notifications': True,
                        'auto_remove_out_of_stock': False,
                        'auto_remove_discontinued': True,
                        'make_public': False,
                    }
                )
                
                # Update fields
                for field, value in input.__dict__.items():
                    if value is not None and hasattr(settings, field):
                        setattr(settings, field, value)
                
                settings.save()
                
                return UpdateWishlistSettings(
                    success=True,
                    message="Wishlist settings updated successfully",
                    settings=settings
                )
                
        except Exception as e:
            return UpdateWishlistSettings(
                success=False, 
                message=str(e)
            )


# Query Class
class WishlistQuery(ObjectType):
    """Wishlist queries"""
    
    my_wishlist = List(WishlistType)
    wishlist_item = Field(WishlistType, id=ID(required=True))
    wishlist_count = Field(Int)
    most_wishlisted_products = List(JSONString)
    wishlist_settings = Field(WishlistSettingsType)
    
    def resolve_my_wishlist(self, info):
        """Get current user's wishlist"""
        if not info.context.user.is_authenticated:
            return []
        
        return Wishlist.objects.active().for_user(info.context.user)
    
    def resolve_wishlist_item(self, info, id):
        """Get specific wishlist item"""
        if not info.context.user.is_authenticated:
            return None
        
        try:
            return Wishlist.objects.get(
                id=id,
                user=info.context.user
            )
        except Wishlist.DoesNotExist:
            return None
    
    def resolve_wishlist_count(self, info):
        """Get wishlist count"""
        if not info.context.user.is_authenticated:
            return 0
        
        return Wishlist.objects.filter(user=info.context.user).count()
    
    def resolve_most_wishlisted_products(self, info):
        """Get most wishlisted products (admin only)"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return []
        
        from api.models.wishlist import Wishlist
        products = Wishlist.objects.most_wishlisted_products(limit=20)
        
        return [
            {
                'product_id': p['product_id'],
                'product_name': p['product__name_ar'],
                'product_price': float(p['product__base_price']),
                'wishlist_count': p['wishlist_count']
            }
            for p in products
        ]
    
    def resolve_wishlist_settings(self, info):
        """Get user wishlist settings"""
        if not info.context.user.is_authenticated:
            return None
        
        try:
            return WishlistSettings.objects.get(user=info.context.user)
        except WishlistSettings.DoesNotExist:
            # Return default settings
            return WishlistSettings(
                user=info.context.user,
                items_per_page=20,
                sort_by='created_at',
                sort_order='desc',
                email_notifications=True,
                push_notifications=True,
                auto_remove_out_of_stock=False,
                auto_remove_discontinued=True,
                make_public=False
            )


# Node Classes from core/schema.py
class WishlistNode(DjangoObjectType, IsAuthenticatedMixin):
    """Enhanced wishlist node with product details"""
    user = Field('UserNode')
    product = Field('ProductNode')
    
    class Meta:
        model = Wishlist
        interfaces = (relay.Node,)
        fields = '__all__'


# Mutation Class
class WishlistMutation(ObjectType):
    """Wishlist mutations"""
    
    toggle_wishlist = ToggleWishlist.Field()
    clear_wishlist = ClearWishlist.Field()
    update_wishlist_item = UpdateWishlistItem.Field()
    move_to_cart = MoveToCart.Field()
    update_wishlist_settings = UpdateWishlistSettings.Field()
