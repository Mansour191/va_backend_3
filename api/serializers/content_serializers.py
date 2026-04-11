"""
Content Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.content import (
    BlogCategory, BlogPost, DesignCategory, Design
)


class BlogCategorySerializer(serializers.ModelSerializer):
    """Blog category serializer"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = [
            'id', 'name_ar', 'name_en', 'slug', 'description',
            'meta_title', 'meta_description', 'image', 'color',
            'sort_order', 'is_active', 'created_at', 'updated_at',
            'post_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_post_count(self, obj):
        """Count published posts in this category"""
        return obj.posts.filter(is_published=True).count()


class BlogPostSerializer(serializers.ModelSerializer):
    """Blog post serializer"""
    category_name = serializers.CharField(source='category.name_ar', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    is_published = serializers.SerializerMethodField()
    get_absolute_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title_ar', 'title_en', 'slug', 'content_ar',
            'content_en', 'summary_ar', 'summary_en', 'category',
            'category_name', 'tags', 'author', 'author_name',
            'guest_author', 'featured_image', 'gallery_images',
            'meta_title', 'meta_description', 'meta_keywords',
            'focus_keyword', 'status', 'is_featured', 'is_top_story',
            'views', 'read_time', 'shares', 'likes',
            'comments_count', 'comments_enabled',
            'comments_require_approval', 'published_at',
            'created_at', 'updated_at', 'is_published',
            'get_absolute_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_published(self, obj):
        """Check if post is published"""
        return obj.is_published
    
    def get_get_absolute_url(self, obj):
        """Get absolute URL for the post"""
        return obj.get_absolute_url()


class DesignCategorySerializer(serializers.ModelSerializer):
    """Design category serializer"""
    design_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignCategory
        fields = [
            'id', 'name_ar', 'name_en', 'slug', 'description',
            'image', 'color_scheme', 'is_active', 'is_featured',
            'sort_order', 'default_prompt_suffix', 'style_keywords',
            'created_at', 'updated_at', 'design_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_design_count(self, obj):
        """Count designs in this category"""
        return obj.designs.filter(status='approved').count()


class DesignSerializer(serializers.ModelSerializer):
    """Design serializer"""
    category_name = serializers.CharField(source='category.name_ar', read_only=True)
    user_name = serializers.CharField(
        source='user.username', read_only=True, allow_null=True
    )
    is_approved = serializers.SerializerMethodField()
    can_download = serializers.SerializerMethodField()
    
    class Meta:
        model = Design
        fields = [
            'id', 'name', 'description', 'image', 'thumbnail',
            'high_res_image', 'category', 'category_name', 'tags',
            'style_keywords', 'user', 'user_name', 'is_anonymous',
            'is_featured', 'is_active', 'is_public', 'status',
            'likes', 'downloads', 'views', 'shares',
            'rating_average', 'rating_count', 'prompt', 'ai_model',
            'generation_parameters', 'generation_time', 'generated_at',
            'file_size', 'resolution', 'file_format', 'color_mode',
            'license_type', 'commercial_use', 'attribution_required',
            'created_at', 'updated_at', 'is_approved', 'can_download'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_approved(self, obj):
        """Check if design is approved"""
        return obj.is_approved
    
    def get_can_download(self, obj):
        """Check if design can be downloaded"""
        return obj.can_download


class BlogPostCreateSerializer(serializers.ModelSerializer):
    """Blog post creation serializer"""
    class Meta:
        model = BlogPost
        fields = [
            'title_ar', 'title_en', 'content_ar', 'content_en',
            'summary_ar', 'summary_en', 'category', 'tags',
            'guest_author', 'featured_image', 'gallery_images',
            'meta_title', 'meta_description', 'meta_keywords',
            'focus_keyword', 'status', 'is_featured',
            'is_top_story', 'comments_enabled',
            'comments_require_approval', 'published_at'
        ]
    
    def validate(self, data):
        """Validate blog post data"""
        if data.get('status') == 'published' and not data.get('published_at'):
            from django.utils import timezone
            data['published_at'] = timezone.now()
        
        return data
    
    def create(self, validated_data):
        """Create blog post"""
        from django.utils.text import slugify
        from django.utils import timezone
        
        # Generate slug if not provided
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['title_en'])
        
        # Auto-generate summaries if not provided
        if not validated_data.get('summary_ar') and validated_data.get('content_ar'):
            content = validated_data['content_ar']
            validated_data['summary_ar'] = content[:200] + '...' if len(content) > 200 else content
        
        if not validated_data.get('summary_en') and validated_data.get('content_en'):
            content = validated_data['content_en']
            validated_data['summary_en'] = content[:200] + '...' if len(content) > 200 else content
        
        # Auto-calculate reading time
        if validated_data.get('content_en'):
            word_count = len(validated_data['content_en'].split())
            validated_data['read_time'] = max(1, word_count // 200)
        
        return BlogPost.objects.create(**validated_data)


class DesignCreateSerializer(serializers.ModelSerializer):
    """Design creation serializer"""
    class Meta:
        model = Design
        fields = [
            'name', 'description', 'image', 'thumbnail',
            'high_res_image', 'category', 'tags', 'style_keywords',
            'is_anonymous', 'is_featured', 'is_active',
            'is_public', 'status', 'prompt', 'ai_model',
            'generation_parameters', 'generation_time',
            'file_size', 'resolution', 'file_format',
            'color_mode', 'license_type', 'commercial_use',
            'attribution_required'
        ]
    
    def create(self, validated_data):
        """Create design"""
        return Design.objects.create(**validated_data)


class BlogPostUpdateSerializer(serializers.ModelSerializer):
    """Blog post update serializer"""
    class Meta:
        model = BlogPost
        fields = [
            'title_ar', 'title_en', 'slug', 'content_ar',
            'content_en', 'summary_ar', 'summary_en', 'category',
            'tags', 'guest_author', 'featured_image',
            'gallery_images', 'meta_title', 'meta_description',
            'meta_keywords', 'focus_keyword', 'status',
            'is_featured', 'is_top_story', 'comments_enabled',
            'comments_require_approval', 'published_at'
        ]
    
    def update(self, instance, validated_data):
        """Update blog post"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DesignUpdateSerializer(serializers.ModelSerializer):
    """Design update serializer"""
    class Meta:
        model = Design
        fields = [
            'name', 'description', 'image', 'thumbnail',
            'high_res_image', 'category', 'tags', 'style_keywords',
            'is_featured', 'is_active', 'is_public', 'status',
            'license_type', 'commercial_use', 'attribution_required'
        ]
    
    def update(self, instance, validated_data):
        """Update design"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ContentBulkActionSerializer(serializers.Serializer):
    """Content bulk action serializer"""
    action = serializers.ChoiceField(
        choices=['publish', 'unpublish', 'feature', 'delete'],
        required=True
    )
    post_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    design_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate(self, data):
        """Validate bulk action data"""
        action = data['action']
        
        if action in ['publish', 'unpublish', 'feature', 'delete'] and not data.get('post_ids') and not data.get('design_ids'):
            raise serializers.ValidationError(
                "post_ids or design_ids required for this action"
            )
        
        return data
    
    def save(self):
        """Execute bulk action"""
        action = self.validated_data['action']
        post_ids = self.validated_data.get('post_ids', [])
        design_ids = self.validated_data.get('design_ids', [])
        
        if post_ids:
            posts = BlogPost.objects.filter(id__in=post_ids)
            
            if action == 'publish':
                posts.update(status='published')
            elif action == 'unpublish':
                posts.update(status='draft')
            elif action == 'feature':
                posts.update(is_featured=True)
            elif action == 'delete':
                posts.delete()
        
        if design_ids:
            designs = Design.objects.filter(id__in=design_ids)
            
            if action == 'publish':
                designs.update(status='approved')
            elif action == 'unpublish':
                designs.update(status='draft')
            elif action == 'feature':
                designs.update(is_featured=True)
            elif action == 'delete':
                designs.delete()
        
        return {
            'status': 'success',
            'action': action,
            'posts_affected': len(post_ids),
            'designs_affected': len(design_ids)
        }
