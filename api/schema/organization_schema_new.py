"""
Organization Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg


class OrganizationType(DjangoObjectType):
    """Organization type"""
    id = graphene.ID(required=True)
    name = String()
    description = String()
    logo = String()
    website = String()
    email = String()
    phone = String()
    
    # Address
    address = String()
    city = String()
    state = String()
    country = String()
    postal_code = String()
    
    # Geographic coordinates
    latitude = Float()
    longitude = Float()
    
    # Settings
    is_active = Boolean()
    is_verified = Boolean()
    timezone = String()
    currency = String()
    language = String()
    
    # Business information
    industry = String()
    size = String()
    revenue = Float()
    employee_count = Int()
    
    # Computed fields
    social_links = List(lambda: SocialType)
    base_wilayas_count = Int()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Organization
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_verified': ['exact'],
            'industry': ['exact'],
            'city': ['exact'],
            'country': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_social_links(self, info):
        """Get social media links"""
        return self.social_platforms.all()


class SocialType(DjangoObjectType):
    """Social media platform type"""
    id = graphene.ID(required=True)
    organization = Field(OrganizationType)
    platform = String()
    platform_type = String()
    url = String()
    handle = String()
    follower_count = Int()
    is_active = Boolean()
    
    # Computed fields
    platform_display = String()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Social
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'organization': ['exact'],
            'platform': ['exact'],
            'platform_type': ['exact'],
            'is_active': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_platform_display(self, info):
        """Get platform display name"""
        return self.get_platform_display()


class PlatformTypeType(DjangoObjectType):
    """Platform type configuration"""
    id = graphene.ID(required=True)
    name = String()
    platform_type = String()
    icon = String()
    color = String()
    base_url = String()
    url_template = String()
    
    # Validation
    is_active = Boolean()
    validation_regex = String()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = PlatformType
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name': ['exact'],
            'platform_type': ['exact'],
            'is_active': ['exact'],
        }


# Input Types
class OrganizationInput(graphene.InputObjectType):
    """Input for organization creation and updates"""
    name = String(required=True)
    description = String()
    logo = String()
    website = String()
    email = String()
    phone = String()
    
    # Address
    address = String()
    city = String()
    state = String()
    country = String()
    postal_code = String()
    
    # Geographic coordinates
    latitude = Float()
    longitude = Float()
    
    # Settings
    is_active = Boolean(default_value=True)
    timezone = String()
    currency = String()
    language = String()
    
    # Business information
    industry = String()
    size = String()
    revenue = Float()
    employee_count = Int()


class SocialInput(graphene.InputObjectType):
    """Input for social media platform creation and updates"""
    organization_id = ID(required=True)
    platform = String(required=True)
    platform_type = String(required=True)
    url = String(required=True)
    handle = String()
    follower_count = Int()
    is_active = Boolean(default_value=True)


class PlatformTypeInput(graphene.InputObjectType):
    """Input for platform type creation and updates"""
    name = String(required=True)
    platform_type = String(required=True)
    icon = String()
    color = String()
    base_url = String()
    url_template = String()
    
    # Validation
    is_active = Boolean(default_value=True)
    validation_regex = String()


# Mutations
class CreateOrganization(Mutation):
    """Create a new organization"""
    
    class Arguments:
        input = OrganizationInput(required=True)

    success = Boolean()
    message = String()
    organization = Field(OrganizationType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.organization import Organization
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateOrganization(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            organization = Organization.objects.create(**input)
            
            return CreateOrganization(
                success=True,
                message="Organization created successfully",
                organization=organization
            )
            
        except Exception as e:
            return CreateOrganization(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateOrganization(Mutation):
    """Update an existing organization"""
    
    class Arguments:
        id = ID(required=True)
        input = OrganizationInput(required=True)

    success = Boolean()
    message = String()
    organization = Field(OrganizationType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            from api.models.organization import Organization
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return UpdateOrganization(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            organization = Organization.objects.get(id=id)
            
            for field, value in input.items():
                if hasattr(organization, field):
                    setattr(organization, field, value)
            
            organization.save()
            
            return UpdateOrganization(
                success=True,
                message="Organization updated successfully",
                organization=organization
            )
            
        except Organization.DoesNotExist:
            return UpdateOrganization(
                success=False,
                message="Organization not found",
                errors=["Organization not found"]
            )
        except Exception as e:
            return UpdateOrganization(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateSocial(Mutation):
    """Create a new social media platform"""
    
    class Arguments:
        input = SocialInput(required=True)

    success = Boolean()
    message = String()
    social = Field(SocialType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.organization import Organization, Social
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateSocial(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            organization = Organization.objects.get(id=input['organization_id'])
            social = Social.objects.create(
                organization=organization,
                **{k: v for k, v in input.items() if k != 'organization_id'}
            )
            
            return CreateSocial(
                success=True,
                message="Social platform created successfully",
                social=social
            )
            
        except Exception as e:
            return CreateSocial(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreatePlatformType(Mutation):
    """Create a new platform type"""
    
    class Arguments:
        input = PlatformTypeInput(required=True)

    success = Boolean()
    message = String()
    platform_type = Field(PlatformTypeType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.organization import PlatformType
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreatePlatformType(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            platform_type = PlatformType.objects.create(**input)
            
            return CreatePlatformType(
                success=True,
                message="Platform type created successfully",
                platform_type=platform_type
            )
            
        except Exception as e:
            return CreatePlatformType(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class OrganizationQuery(ObjectType):
    """Organization queries"""
    
    # Organization queries
    organizations = List(OrganizationType)
    organization = Field(OrganizationType, id=ID(required=True))
    active_organizations = List(OrganizationType)
    
    # Social media queries
    social_platforms = List(SocialType)
    social_platform = Field(SocialType, id=ID(required=True))
    organization_social = List(SocialType, organization_id=ID(required=True))
    
    # Platform type queries
    platform_types = List(PlatformTypeType)
    platform_type = Field(PlatformTypeType, id=ID(required=True))
    active_platform_types = List(PlatformTypeType)
    
    def resolve_organizations(self, info):
        """Get all organizations (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Organization.objects.all()
        return []
    
    def resolve_organization(self, info, id):
        """Get organization by ID"""
        user = info.context.user
        try:
            organization = Organization.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return organization
            return None
        except Organization.DoesNotExist:
            return None
    
    def resolve_active_organizations(self, info):
        """Get active organizations"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Organization.objects.filter(is_active=True)
        return Organization.objects.filter(is_active=True)
    
    def resolve_social_platforms(self, info):
        """Get all social media platforms (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Social.objects.all()
        return []
    
    def resolve_social_platform(self, info, id):
        """Get social platform by ID"""
        user = info.context.user
        try:
            social = Social.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return social
            return None
        except Social.DoesNotExist:
            return None
    
    def resolve_organization_social(self, info, organization_id):
        """Get social platforms for specific organization"""
        user = info.context.user
        try:
            organization = Organization.objects.get(id=organization_id)
            if user.is_authenticated and user.is_staff:
                return organization.social_platforms.all()
            return []
        except Organization.DoesNotExist:
            return []
    
    def resolve_platform_types(self, info):
        """Get all platform types (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return PlatformType.objects.all()
        return []
    
    def resolve_platform_type(self, info, id):
        """Get platform type by ID"""
        user = info.context.user
        try:
            platform_type = PlatformType.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return platform_type
            return None
        except PlatformType.DoesNotExist:
            return None
    
    def resolve_active_platform_types(self, info):
        """Get active platform types"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return PlatformType.objects.filter(is_active=True)
        return PlatformType.objects.filter(is_active=True)


# Mutation Class
class OrganizationMutation(ObjectType):
    """Organization mutations"""
    
    create_organization = CreateOrganization.Field()
    update_organization = UpdateOrganization.Field()
    create_social = CreateSocial.Field()
    create_platform_type = CreatePlatformType.Field()
