"""
Enhanced Cart Models for VynilArt API
"""
from django.db import models
from .product import Product, Material
from django.utils import timezone
import json


class CartItemManager(models.Manager):
    """Custom manager for cart items with enhanced query methods"""
    
    def for_user(self, user):
        """Get cart items for a specific user"""
        return self.filter(user=user)
    
    def for_session(self, session_id):
        """Get cart items for a guest session"""
        return self.filter(session_id=session_id, user__isnull=True)
    
    def active(self):
        """Get only active cart items"""
        return self.filter(
            product__is_active=True,
            quantity__gt=0
        ).select_related(
            'product', 'material', 'user', 'wilaya', 'applied_coupon'
        ).prefetch_related('product__images')
    
    def with_price_changes(self):
        """Get cart items with price changes"""
        items = self.active()
        changed_items = []
        
        for item in items:
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
                item.price_changed = True
                item.current_unit_price = current_unit_price
                item.current_material_price = current_material_price
                changed_items.append(item)
        
        return changed_items
    
    def merge_guest_cart(self, session_id, user):
        """Merge guest cart with user cart"""
        guest_items = self.for_session(session_id)
        user_items = self.for_user(user)
        
        for guest_item in guest_items:
            # Check if similar item exists in user cart
            existing_item = user_items.filter(
                product=guest_item.product,
                material=guest_item.material,
                width=guest_item.width,
                height=guest_item.height
            ).first()
            
            if existing_item:
                # Merge quantities
                existing_item.quantity += guest_item.quantity
                existing_item.options.update(guest_item.options)
                existing_item.save()
                guest_item.delete()
            else:
                # Transfer to user cart
                guest_item.user = user
                guest_item.session_id = None
                guest_item.save()
        
        return user_items


class CartItem(models.Model):
    """
    Cart item model matching api_cartitem table
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE, 
        related_name='cart_items',
        db_column='user_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    material = models.ForeignKey(
        Material, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='material_id'
    )
    quantity = models.IntegerField(default=1)
    options = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_cartitem'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['material']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name_ar}"
