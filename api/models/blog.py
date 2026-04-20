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
    description_ar = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=100, blank=True, null=True)
    order_priority = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_blogcategory'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['order_priority']),
            models.Index(fields=['is_featured']),
        ]
        ordering = ['order_priority', 'name_ar']

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
    excerpt = models.TextField(blank=True, null=True, help_text="Brief summary of the blog post")
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
    featured_image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL to the featured image")
    tags = models.JSONField(default=list, blank=True)
    view_count = models.IntegerField(default=0, help_text="Number of times this post has been viewed")
    views = models.IntegerField(default=0)  # Keep for backward compatibility
    is_published = models.BooleanField(default=False, help_text="Whether this post is published")
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="When this post is scheduled to be published")
    published_at = models.DateTimeField(blank=True, null=True)
    read_time_minutes = models.IntegerField(default=0, help_text="Estimated reading time in minutes")
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
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['views']),
            models.Index(fields=['view_count']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title_ar

    def increment_view_count(self):
        """
        Increment the view count for this blog post
        """
        self.view_count += 1
        self.views += 1  # Keep backward compatibility
        self.save(update_fields=['view_count', 'views'])

    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate read time if not set
        """
        if not self.read_time_minutes:
            # Estimate reading time based on content length
            # Average reading speed: ~200 words per minute
            content_length = len(self.content_ar or self.content_en or '')
            estimated_words = content_length / 5  # Rough estimate: 5 characters per word
            self.read_time_minutes = max(1, round(estimated_words / 200))
        
        super().save(*args, **kwargs)
