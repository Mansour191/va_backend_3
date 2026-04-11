"""
Review and Design Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .product import Product


class Review(models.Model):
    """
    Review model matching api_review table
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_review'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name_ar} ({self.rating} stars)"


class ReviewReport(models.Model):
    """
    Review report model matching api_reviewreport table
    """
    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE,
        db_column='review_id'
    )
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_reviewreport'
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['review', 'user']

    def __str__(self):
        return f"Report by {self.user.username} on {self.review.product.name_ar}"


class DesignCategory(models.Model):
    """
    Design category model matching api_designcategory table
    """
    id = models.AutoField(primary_key=True)
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    design_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_designcategory'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['design_count']),
        ]
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar


class Design(models.Model):
    """
    Design model matching api_design table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(
        DesignCategory, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='category_id'
    )
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='user_id'
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    likes = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, default='pending')
    generated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_design'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['user']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_active']),
            models.Index(fields=['status']),
            models.Index(fields=['likes']),
            models.Index(fields=['downloads']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name
