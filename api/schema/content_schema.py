"""
Content Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg
from django.utils.text import slugify
from api.models.review import Review, ReviewReport, DesignCategory, Design
from api.models.blog import BlogCategory, BlogPost
from api.models.notification import Notification
from api.models.erpnext import ERPNextSyncLog
from api.models.conversation import ConversationHistory
from api.models.dashboard import DashboardSettings
from api.models.wishlist import WishlistSettings
from api.schema.user_schema import UserType
from api.schema.product_schema import ProductType


class BlogCategoryType(DjangoObjectType):
    """Blog category type"""
    id = graphene.ID(required=True)
    name_ar = String()
    name_en = String()
    slug = String()
    description = String()
    description_ar = String()
    
    # SEO and metadata
    meta_title = String()
    meta_description = String()
    
    # Visual
    icon_class = String()
    image = String()
    color = String()
    
    # Organization
    order_priority = Int()
    sort_order = Int()
    is_featured = Boolean()
    is_active = Boolean()
    
    # Computed fields
    post_count = Field(Int)
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = BlogCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_featured': ['exact'],
            'order_priority': ['exact'],
            'sort_order': ['exact'],
        }

    def resolve_post_count(self, info):
        """Count of published posts in this category"""
        return self.posts.filter(is_published=True).count()


class BlogPostType(DjangoObjectType):
    """Blog post type"""
    id = graphene.ID(required=True)
    title_ar = String()
    title_en = String()
    slug = String()
    
    # Content
    content_ar = String()
    content_en = String()
    excerpt = String()
    summary_ar = String()
    summary_en = String()
    
    # Categorization
    category = Field(BlogCategoryType)
    tags = List(String)
    
    # Author and attribution
    author = Field(lambda: UserType)
    guest_author = String()
    
    # Media
    featured_image = String()
    featured_image_url = String()
    gallery_images = List(String)
    
    # SEO and metadata
    meta_title = String()
    meta_description = String()
    meta_keywords = List(String)
    focus_keyword = String()
    
    # Publishing
    status = String()
    is_published = Boolean()
    is_featured = Boolean()
    is_top_story = Boolean()
    scheduled_at = DateTime()
    
    # Analytics
    views = Int()
    view_count = Int()
    read_time_minutes = Int()
    read_time = Int()
    shares = Int()
    likes = Int()
    comments_count = Int()
    
    # Comments settings
    comments_enabled = Boolean()
    comments_require_approval = Boolean()
    
    # Timestamps
    published_at = DateTime()
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = BlogPost
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'title_ar': ['exact', 'icontains'],
            'title_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'category': ['exact'],
            'author': ['exact'],
            'status': ['exact'],
            'is_published': ['exact'],
            'is_featured': ['exact'],
            'is_top_story': ['exact'],
            'scheduled_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'published_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_published(self, info):
        """Check if post is published"""
        from django.utils import timezone
        return (
            self.status == 'published' and (
                self.published_at is None or 
                self.published_at <= timezone.now()
            )
        )

    def resolve_get_absolute_url(self, info):
        """Get absolute URL for post"""
        return f"/blog/{self.slug}/"


class DesignCategoryType(DjangoObjectType):
    """Design category type"""
    id = graphene.ID(required=True)
    name_ar = String()
    name_en = String()
    slug = String()
    description = String()
    
    # Visual
    image = String()
    color_scheme = List(String)
    
    # Settings
    is_active = Boolean()
    is_featured = Boolean()
    sort_order = Int()
    
    # AI generation settings
    default_prompt_suffix = String()
    style_keywords = List(String)
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = DesignCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'is_featured': ['exact'],
        }


class DesignType(DjangoObjectType):
    """Design type"""
    id = graphene.ID(required=True)
    name = String()
    description = String()
    
    # Visual assets
    image = String()
    thumbnail = String()
    high_res_image = String()
    
    # Categorization
    category = Field(DesignCategoryType)
    tags = List(String)
    style_keywords = List(String)
    
    # User and attribution
    user = Field(lambda: UserType)
    is_anonymous = Boolean()
    
    # Status and visibility
    is_featured = Boolean()
    is_active = Boolean()
    is_public = Boolean()
    status = String()
    
    # Engagement metrics
    likes = Int()
    downloads = Int()
    views = Int()
    shares = Int()
    rating_average = Float()
    rating_count = Int()
    
    # AI generation metadata
    prompt = String()
    ai_model = String()
    generation_parameters = JSONString()
    generation_time = Float()
    generated_at = DateTime()
    
    # Technical specifications
    file_size = Int()
    resolution = String()
    file_format = String()
    color_mode = String()
    
    # Licensing and usage
    license_type = String()
    commercial_use = Boolean()
    attribution_required = Boolean()
    
    # Computed fields
    is_approved = Boolean()
    can_download = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Design
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'category': ['exact'],
            'user': ['exact'],
            'status': ['exact'],
            'is_featured': ['exact'],
            'is_active': ['exact'],
            'is_public': ['exact'],
            'license_type': ['exact'],
            'tags': ['exact'],
            'generated_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_approved(self, info):
        """Check if design is approved"""
        return self.status == 'approved'

    def resolve_can_download(self, info):
        """Check if design can be downloaded"""
        return self.is_approved and self.is_active and self.is_public


# Input Types
class BlogCategoryInput(graphene.InputObjectType):
    """Input for blog category creation and updates"""
    name_ar = String(required=True)
    name_en = String(required=True)
    description = String()
    description_ar = String()
    
    # SEO and metadata
    meta_title = String()
    meta_description = String()
    
    # Visual
    icon_class = String()
    image = String()
    color = String()
    
    # Organization
    order_priority = Int(default_value=0)
    sort_order = Int(default_value=0)
    is_featured = Boolean(default_value=False)
    is_active = Boolean(default_value=True)


class BlogPostInput(graphene.InputObjectType):
    """Input for blog post creation and updates"""
    title_ar = String(required=True)
    title_en = String(required=True)
    
    # Content
    content_ar = String(required=True)
    content_en = String(required=True)
    excerpt = String()
    summary_ar = String()
    summary_en = String()
    
    # Categorization
    category_id = ID()
    tags = List(String)
    
    # Author and attribution
    guest_author = String()
    
    # Media
    featured_image = String()
    featured_image_url = String()
    gallery_images = List(String)
    
    # SEO and metadata
    meta_title = String()
    meta_description = String()
    meta_keywords = List(String)
    focus_keyword = String()
    
    # Publishing
    status = String()
    is_published = Boolean()
    is_featured = Boolean()
    is_top_story = Boolean()
    scheduled_at = DateTime()
    
    # Comments settings
    comments_enabled = Boolean(default_value=True)
    comments_require_approval = Boolean(default_value=True)
    
    # Scheduling
    published_at = DateTime()


class DesignCategoryInput(graphene.InputObjectType):
    """Input for design category creation and updates"""
    name_ar = String(required=True)
    name_en = String(required=True)
    description = String()
    
    # Visual
    image = String()
    color_scheme = List(String)
    
    # Settings
    is_active = Boolean(default_value=True)
    is_featured = Boolean(default_value=False)
    sort_order = Int(default_value=0)
    
    # AI generation settings
    default_prompt_suffix = String()
    style_keywords = List(String)


class DesignInput(graphene.InputObjectType):
    """Input for design creation and updates"""
    name = String(required=True)
    description = String()
    
    # Visual assets
    image = String()
    thumbnail = String()
    high_res_image = String()
    
    # Categorization
    category_id = ID()
    tags = List(String)
    style_keywords = List(String)
    
    # User and attribution
    is_anonymous = Boolean(default_value=False)
    
    # Status and visibility
    is_featured = Boolean(default_value=False)
    is_active = Boolean(default_value=True)
    is_public = Boolean(default_value=True)
    status = String()
    
    # AI generation metadata
    prompt = String()
    ai_model = String()
    generation_parameters = JSONString()
    generation_time = Float()
    
    # Technical specifications
    file_size = Int()
    resolution = String()
    file_format = String(default_value='PNG')
    color_mode = String()
    
    # Licensing and usage
    license_type = String(default_value='free')
    commercial_use = Boolean(default_value=True)
    attribution_required = Boolean(default_value=False)


# Mutations
class CreateBlogCategory(Mutation):
    """Create a new blog category"""
    
    class Arguments:
        input = BlogCategoryInput(required=True)

    success = Boolean()
    message = String()
    blog_category = Field(BlogCategoryType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            # Generate slug if not provided
            if 'slug' not in input:
                input['slug'] = slugify(input['name_en'])
            
            blog_category = BlogCategory.objects.create(**input)
            
            return CreateBlogCategory(
                success=True,
                message="Blog category created successfully",
                blog_category=blog_category
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
    blog_category = Field(BlogCategoryType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            blog_category = BlogCategory.objects.get(id=id)
            
            # Update slug if name_en changed and slug not provided
            if 'name_en' in input and 'slug' not in input:
                input['slug'] = slugify(input['name_en'])
            
            for field, value in input.items():
                setattr(blog_category, field, value)
            
            blog_category.save()
            
            return UpdateBlogCategory(
                success=True,
                message="Blog category updated successfully",
                blog_category=blog_category
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


class DeleteBlogCategory(Mutation):
    """Delete a blog category"""
    
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()
    errors = List(String)

    def mutate(self, info, id):
        try:
            blog_category = BlogCategory.objects.get(id=id)
            blog_category.delete()
            
            return DeleteBlogCategory(
                success=True,
                message="Blog category deleted successfully"
            )
            
        except BlogCategory.DoesNotExist:
            return DeleteBlogCategory(
                success=False,
                message="Blog category not found",
                errors=["Blog category not found"]
            )
        except Exception as e:
            return DeleteBlogCategory(
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
    blog_post = Field(BlogPostType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.blog import BlogCategory
            
            user = info.context.user
            
            # Generate slug if not provided
            if 'slug' not in input:
                input['slug'] = slugify(input['title_en'])
            
            # Handle category
            category = None
            if 'category_id' in input:
                category = BlogCategory.objects.get(id=input['category_id'])
            
            # Auto-generate summaries if not provided
            if 'summary_ar' not in input and 'content_ar' in input:
                content = input['content_ar']
                input['summary_ar'] = content[:200] + '...' if len(content) > 200 else content
            
            if 'summary_en' not in input and 'content_en' in input:
                content = input['content_en']
                input['summary_en'] = content[:200] + '...' if len(content) > 200 else content
            
            # Auto-calculate reading time
            if 'content_en' in input:
                word_count = len(input['content_en'].split())
                input['read_time'] = max(1, word_count // 200)
            
            blog_post = BlogPost.objects.create(
                author=user,
                category=category,
                **input
            )
            
            return CreateBlogPost(
                success=True,
                message="Blog post created successfully",
                blog_post=blog_post
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
    blog_post = Field(BlogPostType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            user = info.context.user
            
            blog_post = BlogPost.objects.get(id=id)
            
            # Check permissions
            if not user.is_staff and blog_post.author != user:
                return UpdateBlogPost(
                    success=False,
                    message="Permission denied",
                    errors=["You can only update your own blog posts"]
                )
            
            # Handle category
            if 'category_id' in input:
                category = BlogCategory.objects.get(id=input['category_id'])
                input['category'] = category
                del input['category_id']
            
            # Update slug if title_en changed and slug not provided
            if 'title_en' in input and 'slug' not in input:
                input['slug'] = slugify(input['title_en'])
            
            # Auto-generate excerpt if not provided
            if 'excerpt' not in input:
                content = input.get('content_en') or blog_post.content_en
                if content:
                    input['excerpt'] = content[:300] + '...' if len(content) > 300 else content
            
            # Auto-calculate reading time if content changed
            if 'content_en' in input:
                word_count = len(input['content_en'].split())
                input['read_time_minutes'] = max(1, word_count // 200)
            
            for field, value in input.items():
                setattr(blog_post, field, value)
            
            blog_post.save()
            
            return UpdateBlogPost(
                success=True,
                message="Blog post updated successfully",
                blog_post=blog_post
            )
            
        except BlogPost.DoesNotExist:
            return UpdateBlogPost(
                success=False,
                message="Blog post not found",
                errors=["Blog post not found"]
            )
        except Exception as e:
            return UpdateBlogPost(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class IncrementBlogPostViewCount(Mutation):
    """Increment view count for a blog post"""
    
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()
    view_count = Int()

    def mutate(self, info, id):
        try:
            blog_post = BlogPost.objects.get(id=id)
            blog_post.increment_view_count()
            
            return IncrementBlogPostViewCount(
                success=True,
                message="View count incremented successfully",
                view_count=blog_post.view_count
            )
            
        except BlogPost.DoesNotExist:
            return IncrementBlogPostViewCount(
                success=False,
                message="Blog post not found",
                view_count=0
            )
        except Exception as e:
            return IncrementBlogPostViewCount(
                success=False,
                message=str(e),
                view_count=0
            )


class CreateDesignCategory(Mutation):
    """Create a new design category"""
    
    class Arguments:
        input = DesignCategoryInput(required=True)

    success = Boolean()
    message = String()
    design_category = Field(DesignCategoryType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            # Generate slug if not provided
            if 'slug' not in input:
                input['slug'] = slugify(input['name_en'])
            
            design_category = DesignCategory.objects.create(**input)
            
            return CreateDesignCategory(
                success=True,
                message="Design category created successfully",
                design_category=design_category
            )
            
        except Exception as e:
            return CreateDesignCategory(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateDesign(Mutation):
    """Create a new design"""
    
    class Arguments:
        input = DesignInput(required=True)

    success = Boolean()
    message = String()
    design = Field(DesignType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.design import DesignCategory
            
            user = info.context.user
            
            # Handle category
            category = None
            if 'category_id' in input:
                category = DesignCategory.objects.get(id=input['category_id'])
            
            design = Design.objects.create(
                user=user,
                category=category,
                **input
            )
            
            return CreateDesign(
                success=True,
                message="Design created successfully",
                design=design
            )
            
        except Exception as e:
            return CreateDesign(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class ContentQuery(ObjectType):
    """Content queries"""
    
    # Blog queries
    blog_categories = List(BlogCategoryType)
    blog_category = Field(BlogCategoryType, id=ID(required=True))
    blog_posts = List(BlogPostType)
    blog_post = Field(BlogPostType, id=ID(required=True))
    featured_blog_posts = List(BlogPostType)
    published_blog_posts = List(BlogPostType)
    
    # Design queries
    design_categories = List(DesignCategoryType)
    design_category = Field(DesignCategoryType, id=ID(required=True))
    designs = List(DesignType)
    design = Field(DesignType, id=ID(required=True))
    featured_designs = List(DesignType)
    approved_designs = List(DesignType)
    
    # ERPNext sync queries - commented out due to class definition order
    # sync_logs = List(ERPNextSyncLogNode, limit=Int(default=50), status=String())
    
    def resolve_blog_categories(self, info):
        """Get all blog categories ordered by priority and name"""
        return BlogCategory.objects.filter(is_active=True).order_by('order_priority', 'name_ar')
    
    def resolve_blog_category(self, info, id):
        """Get blog category by ID"""
        try:
            return BlogCategory.objects.get(id=id)
        except BlogCategory.DoesNotExist:
            return None
    
    def resolve_blog_posts(self, info):
        """Get all blog posts"""
        return BlogPost.objects.all()
    
    def resolve_blog_post(self, info, id):
        """Get blog post by ID"""
        try:
            return BlogPost.objects.get(id=id)
        except BlogPost.DoesNotExist:
            return None
    
    def resolve_featured_blog_posts(self, info):
        """Get featured blog posts"""
        return BlogPost.objects.filter(is_featured=True, is_published=True)
    
    def resolve_published_blog_posts(self, info):
        """Get published blog posts"""
        from django.utils import timezone
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        )
    
    def resolve_design_categories(self, info):
        """Get all design categories"""
        return DesignCategory.objects.filter(is_active=True)
    
    def resolve_design_category(self, info, id):
        """Get design category by ID"""
        try:
            return DesignCategory.objects.get(id=id)
        except DesignCategory.DoesNotExist:
            return None
    
    def resolve_designs(self, info):
        """Get all designs"""
        return Design.objects.all()
    
    def resolve_design(self, info, id):
        """Get design by ID"""
        try:
            return Design.objects.get(id=id)
        except Design.DoesNotExist:
            return None
    
    def resolve_featured_designs(self, info):
        """Get featured designs"""
        return Design.objects.filter(is_featured=True, is_approved=True)
    
    def resolve_approved_designs(self, info):
        """Get approved designs"""
        return Design.objects.filter(status='approved', is_active=True, is_public=True)
    
    def resolve_sync_logs(self, info, limit=50, status=None):
        """Get ERPNext sync logs with optional status filtering
        Optimized for memory efficiency with limits and selective field loading
        """
        from api.utils.erpnext_helper import ERPNextSyncHelper
        
        # Validate limit to prevent memory issues
        limit = min(max(limit, 1), 100)  # Ensure limit is between 1 and 100
        
        return ERPNextSyncHelper.get_recent_logs(limit=limit, status_filter=status)


# Mutation Class
class ContentMutation(ObjectType):
    """Content mutations"""
    
    create_blog_category = CreateBlogCategory.Field()
    update_blog_category = UpdateBlogCategory.Field()
    delete_blog_category = DeleteBlogCategory.Field()
    create_blog_post = CreateBlogPost.Field()
    update_blog_post = UpdateBlogPost.Field()
    increment_blog_post_view_count = IncrementBlogPostViewCount.Field()
    create_design_category = CreateDesignCategory.Field()
    create_design = CreateDesign.Field()


# Node Classes from core/schema.py
class ReviewNode(DjangoObjectType):
    """Review node with product details"""
    user = Field(lambda: UserType)
    product = Field(lambda: ProductType)
    
    class Meta:
        model = Review
        interfaces = (relay.Node,)
        fields = '__all__'


class ReviewReportNode(DjangoObjectType):
    """Review report node"""
    class Meta:
        model = ReviewReport
        interfaces = (relay.Node,)
        fields = '__all__'


class DesignCategoryNode(DjangoObjectType):
    """Design category node"""
    class Meta:
        model = DesignCategory
        interfaces = (relay.Node,)
        fields = '__all__'


class DesignNode(DjangoObjectType):
    """Design node with category relationship"""
    category = Field(lambda: DesignCategoryNode)
    
    class Meta:
        model = Design
        interfaces = (relay.Node,)
        fields = '__all__'


class BlogCategoryNode(DjangoObjectType):
    """Blog category node"""
    class Meta:
        model = BlogCategory
        interfaces = (relay.Node,)
        fields = '__all__'


class BlogPostNode(DjangoObjectType):
    """Blog post node with category relationship"""
    category = Field(lambda: BlogCategoryNode)
    
    class Meta:
        model = BlogPost
        interfaces = (relay.Node,)
        fields = '__all__'


class NotificationNode(DjangoObjectType):
    """Notification node with enhanced filtering"""
    class Meta:
        model = Notification
        interfaces = (relay.Node,)
        fields = '__all__'


class ERPNextSyncLogNode(DjangoObjectType):
    """ERPNext sync log node"""
    class Meta:
        model = ERPNextSyncLog
        interfaces = (relay.Node,)
        fields = '__all__'


class ConversationHistoryNode(DjangoObjectType):
    """Conversation history node"""
    class Meta:
        model = ConversationHistory
        interfaces = (relay.Node,)
        fields = '__all__'


class DashboardSettingsNode(DjangoObjectType):
    """Dashboard settings node"""
    class Meta:
        model = DashboardSettings
        interfaces = (relay.Node,)
        fields = '__all__'


class WishlistSettingsNode(DjangoObjectType):
    """Wishlist settings node"""
    class Meta:
        model = WishlistSettings
        interfaces = (relay.Node,)
        fields = '__all__'
