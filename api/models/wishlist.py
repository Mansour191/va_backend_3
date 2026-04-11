"""
Enhanced Wishlist Models for VynilArt API
"""
from django.db import models
from .product import Product
from django.utils import timezone
import json


class WishlistManager(models.Manager):
    """Custom manager for wishlist items with enhanced query methods"""
    
    def for_user(self, user):
        """Get wishlist items for a specific user"""
        return self.filter(user=user)
    
    def active(self):
        """Get only active wishlist items"""
        return self.filter(
            product__is_active=True
        ).select_related(
            'product', 'user'
        ).prefetch_related('product__images')
    
    def with_product_details(self):
        """Get wishlist items with enhanced product details"""
        return self.active().annotate(
            product_name=models.F('product__name_ar'),
            product_price=models.F('product__base_price'),
            product_stock=models.F('product__stock'),
            product_is_active=models.F('product__is_active'),
            product_images=models.F('product__images')
        )
    
    def most_wishlisted_products(self, limit=10):
        """Get most wishlisted products across all users"""
        from django.db.models import Count
        return self.values(
            'product_id', 'product__name_ar', 'product__base_price'
        ).annotate(
            wishlist_count=Count('id')
        ).filter(
            product__is_active=True
        ).order_by('-wishlist_count')[:limit]


class Wishlist(models.Model):
    """
    Wishlist model matching api_wishlist table
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE, 
        related_name='wishlist_items',
        db_column='user_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='wishlist_entries',
        db_column='product_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_wishlist'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name_ar}"


class WishlistSettings(models.Model):
    """User wishlist settings and preferences"""
    
    user = models.OneToOneField(
        'api.User', 
        on_delete=models.CASCADE, 
        related_name='wishlist_settings'
    )
    
    # Display preferences
    items_per_page = models.IntegerField(
        default=20,
        help_text="Number of items to display per page"
    )
    sort_by = models.CharField(
        max_length=20,
        choices=[
            ('created_at', 'Date Added'),
            ('priority', 'Priority'),
            ('product__name_ar', 'Product Name'),
            ('product__base_price', 'Price'),
        ],
        default='created_at',
        help_text="Default sort order"
    )
    sort_order = models.CharField(
        max_length=4,
        choices=[
            ('asc', 'Ascending'),
            ('desc', 'Descending'),
        ],
        default='desc',
        help_text="Sort direction"
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Enable email notifications for wishlist updates"
    )
    push_notifications = models.BooleanField(
        default=True,
        help_text="Enable push notifications for wishlist updates"
    )
    
    # Auto-cleanup preferences
    auto_remove_out_of_stock = models.BooleanField(
        default=False,
        help_text="Automatically remove out-of-stock items"
    )
    auto_remove_discontinued = models.BooleanField(
        default=True,
        help_text="Automatically remove discontinued products"
    )
    
    # Privacy settings
    make_public = models.BooleanField(
        default=False,
        help_text="Make wishlist publicly visible"
    )
    share_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Token for sharing wishlist"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wishlist Settings'
        verbose_name_plural = 'Wishlist Settings'

    def __str__(self):
        return f"{self.user.username} Wishlist Settings"

    def generate_share_token(self):
        """Generate a unique share token"""
        import uuid
        self.share_token = uuid.uuid4().hex
        self.save()
        return self.share_token

    def get_share_url(self):
        """Get the share URL for this wishlist"""
        if self.share_token:
            return f"/wishlist/shared/{self.share_token}"
        return None
