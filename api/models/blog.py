"""
Blog Models for VynilArt API
"""
from django.db import models


class BlogCategory(models.Model):
    """
    Blog category model matching api_blogcategory table
    """
    id = models.AutoField(primary_key=True)
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_blogcategory'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar


class BlogPost(models.Model):
    """
    Blog post model matching api_blogpost table
    """
    id = models.AutoField(primary_key=True)
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    content_ar = models.TextField()
    content_en = models.TextField()
    summary_ar = models.TextField(blank=True, null=True)
    summary_en = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        BlogCategory, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='category_id'
    )
    author = models.ForeignKey(
        'api.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='author_id'
    )
    featured_image = models.CharField(max_length=500, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    views = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_blogpost'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['author']),
            models.Index(fields=['is_published']),
            models.Index(fields=['published_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['views']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title_ar
