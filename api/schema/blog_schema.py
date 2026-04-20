"""
Blog Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg

from api.models.blog import BlogCategory, BlogPost


class BlogCategoryType(DjangoObjectType):
    """Blog category type"""
    # Computed fields
    post_count = Field(Int)

    class Meta:
        model = BlogCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_featured': ['exact'],
        }

    def resolve_post_count(self, info):
        """Count posts in this category"""
        return self.posts.filter(is_published=True).count()


class BlogPostType(DjangoObjectType):
    """Blog post type"""
    # Computed fields
    reading_time = Field(Int)

    class Meta:
        model = BlogPost
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'title_ar': ['exact', 'icontains'],
            'title_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_published': ['exact'],
            'category': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_reading_time(self, info):
        """Calculate estimated reading time in minutes"""
        content = self.content_ar or self.content_en or ''
        word_count = len(content.split())
        return max(1, word_count // 200)  # Assume 200 words per minute


# Input Types
class BlogCategoryInput(graphene.InputObjectType):
    """Input for blog category creation and updates"""
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String()
    description_ar = String()
    description_en = String()
    image = String()
    is_active = Boolean()
    sort_order = Int()
    meta_title = String()
    meta_description = String()


class BlogPostInput(graphene.InputObjectType):
    """Input for blog post creation and updates"""
    title_ar = String(required=True)
    title_en = String(required=True)
    slug = String()
    excerpt_ar = String()
    excerpt_en = String()
    content_ar = String()
    content_en = String()
    featured_image = String()
    is_published = Boolean()
    is_featured = Boolean()
    sort_order = Int()
    category_id = ID()
    tags = List(String)
    meta_title = String()
    meta_description = String()
    meta_keywords = List(String)


# Mutations
class CreateBlogCategory(Mutation):
    """Create a new blog category"""
    
    class Arguments:
        input = BlogCategoryInput(required=True)

    success = Boolean()
    message = String()
    category = Field(BlogCategoryType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            category = BlogCategory.objects.create(**input)
            
            return CreateBlogCategory(
                success=True,
                message="Blog category created successfully",
                category=category
            )
            
        except Exception as e:
            return CreateBlogCategory(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateBlogCategory(Mutation):
    """Update an existing blog category"""
    
    class Arguments:
        id = ID(required=True)
        input = BlogCategoryInput(required=True)

    success = Boolean()
    message = String()
    category = Field(BlogCategoryType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            category = BlogCategory.objects.get(id=id)
            
            for field, value in input.items():
                if hasattr(category, field):
                    setattr(category, field, value)
            
            category.save()
            
            return UpdateBlogCategory(
                success=True,
                message="Blog category updated successfully",
                category=category
            )
            
        except BlogCategory.DoesNotExist:
            return UpdateBlogCategory(
                success=False,
                message="Blog category not found",
                errors=["Blog category not found"]
            )
        except Exception as e:
            return UpdateBlogCategory(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateBlogPost(Mutation):
    """Create a new blog post"""
    
    class Arguments:
        input = BlogPostInput(required=True)

    success = Boolean()
    message = String()
    post = Field(BlogPostType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            # Handle category
            category = None
            if 'category_id' in input:
                category = BlogCategory.objects.get(id=input['category_id'])
                del input['category_id']
            
            post = BlogPost.objects.create(category=category, **input)
            
            return CreateBlogPost(
                success=True,
                message="Blog post created successfully",
                post=post
            )
            
        except BlogCategory.DoesNotExist:
            return CreateBlogPost(
                success=False,
                message="Blog category not found",
                errors=["Blog category not found"]
            )
        except Exception as e:
            return CreateBlogPost(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateBlogPost(Mutation):
    """Update an existing blog post"""
    
    class Arguments:
        id = ID(required=True)
        input = BlogPostInput(required=True)

    success = Boolean()
    message = String()
    post = Field(BlogPostType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            post = BlogPost.objects.get(id=id)
            
            # Handle category
            if 'category_id' in input:
                if input['category_id']:
                    post.category = BlogCategory.objects.get(id=input['category_id'])
                else:
                    post.category = None
                del input['category_id']
            
            for field, value in input.items():
                if hasattr(post, field):
                    setattr(post, field, value)
            
            post.save()
            
            return UpdateBlogPost(
                success=True,
                message="Blog post updated successfully",
                post=post
            )
            
        except BlogPost.DoesNotExist:
            return UpdateBlogPost(
                success=False,
                message="Blog post not found",
                errors=["Blog post not found"]
            )
        except BlogCategory.DoesNotExist:
            return UpdateBlogPost(
                success=False,
                message="Blog category not found",
                errors=["Blog category not found"]
            )
        except Exception as e:
            return UpdateBlogPost(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class BlogQuery(ObjectType):
    """Blog queries"""
    
    # Category queries
    blog_categories = List(BlogCategoryType)
    blog_category = Field(BlogCategoryType, id=ID(required=True))
    active_blog_categories = List(BlogCategoryType)
    
    # Post queries
    blog_posts = List(BlogPostType)
    blog_post = Field(BlogPostType, id=ID(required=True))
    published_blog_posts = List(BlogPostType)
    featured_blog_posts = List(BlogPostType)
    category_blog_posts = List(BlogPostType, category_id=ID(required=True))
    
    def resolve_blog_categories(self, info):
        """Get all blog categories"""
        return BlogCategory.objects.all().order_by('sort_order', 'name_ar')
    
    def resolve_blog_category(self, info, id):
        """Get blog category by ID"""
        try:
            return BlogCategory.objects.get(id=id)
        except BlogCategory.DoesNotExist:
            return None
    
    def resolve_active_blog_categories(self, info):
        """Get active blog categories"""
        return BlogCategory.objects.filter(is_active=True).order_by('sort_order', 'name_ar')
    
    def resolve_blog_posts(self, info):
        """Get all blog posts"""
        return BlogPost.objects.all().order_by('-created_at')
    
    def resolve_blog_post(self, info, id):
        """Get blog post by ID"""
        try:
            return BlogPost.objects.get(id=id)
        except BlogPost.DoesNotExist:
            return None
    
    def resolve_published_blog_posts(self, info):
        """Get published blog posts"""
        return BlogPost.objects.filter(is_published=True).order_by('-published_at', '-created_at')
    
    def resolve_featured_blog_posts(self, info):
        """Get featured blog posts"""
        return BlogPost.objects.filter(is_published=True, is_featured=True).order_by('-published_at', '-created_at')
    
    def resolve_category_blog_posts(self, info, category_id):
        """Get blog posts for specific category"""
        try:
            category = BlogCategory.objects.get(id=category_id)
            return category.posts.filter(is_published=True).order_by('-published_at', '-created_at')
        except BlogCategory.DoesNotExist:
            return []


# Mutation Class
class BlogMutation(ObjectType):
    """Blog mutations"""
    
    create_blog_category = CreateBlogCategory.Field()
    update_blog_category = UpdateBlogCategory.Field()
    create_blog_post = CreateBlogPost.Field()
    update_blog_post = UpdateBlogPost.Field()
