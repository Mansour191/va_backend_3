# backend/api/models/product_image.py
# Enhanced ProductImage model with advanced image processing

import os
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from PIL import Image as PILImage


class ProductImageEnhanced(models.Model):
    """
    Enhanced Product images with additional features
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        'api.Product', 
        on_delete=models.CASCADE, 
        related_name='enhanced_images',
        db_column='product_id'
    )
    
    # Basic fields matching SQL schema
    image_url = models.CharField(
        max_length=500,
        help_text='Product image URL'
    )
    alt_text = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Alternative text for SEO and accessibility'
    )
    is_main = models.BooleanField(
        default=False,
        help_text='Mark as main/primary image'
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text='Display order for images'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_productimage'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_main']),
            models.Index(fields=['sort_order']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.product.name_ar} - Image {self.id}"

    def set_as_main(self):
        """Set this image as main and unset others"""
        ProductImage.objects.filter(product=self.product).update(is_main=False)
        self.is_main = True
        self.save()


