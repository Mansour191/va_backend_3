"""
Design Schema for VynilArt API
Contains GraphQL types, queries, and mutations for Design Management
"""
import graphene
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Boolean, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from ..models import Design, DesignCategory

User = get_user_model()


class DesignType(DjangoObjectType):
    """
    GraphQL type for Design model
    """
    image_url = String()
    tags_list = List(String)
    
    class Meta:
        model = Design
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'category': ['exact'],
            'user': ['exact'],
            'is_featured': ['exact'],
            'is_active': ['exact'],
            'status': ['exact'],
            'likes': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_image_url(self, info):
        """
        Resolve full image URL from Django Media settings
        """
        if self.image:
            from django.conf import settings
            if hasattr(settings, 'MEDIA_URL') and self.image:
                return f"{settings.MEDIA_URL}{self.image}"
            return self.image
        return None
    
    def resolve_tags_list(self, info):
        """
        Resolve tags as a list of strings
        """
        if self.tags:
            return self.tags if isinstance(self.tags, list) else []
        return []


class DesignCategoryType(DjangoObjectType):
    """
    GraphQL type for DesignCategory model
    """
    name = String()
    
    class Meta:
        model = DesignCategory
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact', 'icontains'],
            'is_active': ['exact'],
            'design_count': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_name(self, info):
        """
        Resolve name based on current language (fallback to Arabic if English not available)
        """
        language = getattr(info.context, 'LANGUAGE_CODE', 'ar')
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name_ar


class ToggleLikeDesign(Mutation):
    """
    Mutation to toggle like on a design (increment likes count)
    """
    class Arguments:
        id = ID(required=True, description="Design ID to like")
    
    success = Boolean()
    likes = Int()
    design = Field(DesignType)
    
    def mutate(self, info, id):
        """
        Toggle like on design by incrementing likes count
        """
        if not info.context.user.is_authenticated:
            raise Exception("Authentication required")
        
        try:
            design = Design.objects.get(id=id)
            design.likes = F('likes') + 1
            design.save()
            design.refresh_from_db()
            
            return ToggleLikeDesign(
                success=True,
                likes=design.likes,
                design=design
            )
        except Design.DoesNotExist:
            raise Exception("Design not found")


class CreateDesign(Mutation):
    """
    Mutation to create a new design
    """
    class Arguments:
        name = String(required=True)
        description = String()
        image = String()
        category_id = ID()
        tags = List(String)
        status = String(default_value='pending')
        is_featured = Boolean(default_value=False)
    
    design = Field(DesignType)
    success = Boolean()
    
    def mutate(self, info, **kwargs):
        """
        Create a new design
        """
        if not info.context.user.is_authenticated:
            raise Exception("Authentication required")
        
        # Extract category_id from kwargs
        category_id = kwargs.pop('category_id', None)
        tags = kwargs.pop('tags', [])
        
        design = Design.objects.create(
            user=info.context.user,
            category_id=category_id,
            tags=tags,
            **kwargs
        )
        
        return CreateDesign(
            design=design,
            success=True
        )


class UpdateDesign(Mutation):
    """
    Mutation to update an existing design
    """
    class Arguments:
        id = ID(required=True)
        name = String()
        description = String()
        image = String()
        category_id = ID()
        tags = List(String)
        status = String()
        is_featured = Boolean()
        is_active = Boolean()
    
    design = Field(DesignType)
    success = Boolean()
    
    def mutate(self, info, id, **kwargs):
        """
        Update an existing design
        """
        if not info.context.user.is_authenticated:
            raise Exception("Authentication required")
        
        try:
            design = Design.objects.get(id=id)
            
            # Check if user is the owner or staff
            if design.user != info.context.user and not info.context.user.is_staff:
                raise Exception("Permission denied")
            
            # Extract category_id from kwargs
            category_id = kwargs.pop('category_id', None)
            if category_id is not None:
                design.category_id = category_id
            
            # Update fields
            for field, value in kwargs.items():
                if field == 'tags' and isinstance(value, list):
                    design.tags = value
                else:
                    setattr(design, field, value)
            
            design.save()
            
            return UpdateDesign(
                design=design,
                success=True
            )
        except Design.DoesNotExist:
            raise Exception("Design not found")


class DeleteDesign(Mutation):
    """
    Mutation to delete a design
    """
    class Arguments:
        id = ID(required=True)
    
    success = Boolean()
    
    def mutate(self, info, id):
        """
        Delete a design
        """
        if not info.context.user.is_authenticated:
            raise Exception("Authentication required")
        
        try:
            design = Design.objects.get(id=id)
            
            # Check if user is the owner or staff
            if design.user != info.context.user and not info.context.user.is_staff:
                raise Exception("Permission denied")
            
            design.delete()
            
            return DeleteDesign(success=True)
        except Design.DoesNotExist:
            raise Exception("Design not found")


class DesignQuery(ObjectType):
    """
    Design-related queries
    """
    designs = DjangoFilterConnectionField(DesignType)
    design = Field(DesignType, id=ID(required=True))
    featured_designs = List(DesignType)
    designs_by_tags = List(DesignType, tags=List(String, required=True))
    my_designs = List(DesignType)
    
    def resolve_featured_designs(self, info):
        """
        Get all featured designs (is_featured=1)
        """
        return Design.objects.filter(
            is_featured=True,
            is_active=True,
            status='approved'
        ).order_by('-likes', '-created_at')
    
    def resolve_designs_by_tags(self, info, tags):
        """
        Get designs that contain any of the specified tags
        """
        if not tags:
            return Design.objects.none()
        
        q_objects = Q()
        for tag in tags:
            q_objects |= Q(tags__contains=[tag])
        
        return Design.objects.filter(
            q_objects,
            is_active=True,
            status='approved'
        ).distinct().order_by('-created_at')
    
    def resolve_my_designs(self, info):
        """
        Get designs for the current authenticated user
        """
        if not info.context.user.is_authenticated:
            return Design.objects.none()
        
        return Design.objects.filter(
            user=info.context.user
        ).order_by('-created_at')


class DesignMutation(ObjectType):
    """
    Design-related mutations
    """
    toggle_like_design = ToggleLikeDesign.Field()
    create_design = CreateDesign.Field()
    update_design = UpdateDesign.Field()
    delete_design = DeleteDesign.Field()
