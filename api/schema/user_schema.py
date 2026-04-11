"""
User Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Boolean, DateTime, ID, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from api.models.user import UserProfile

User = get_user_model()


class GroupType(DjangoObjectType):
    """
    Django Group type for RBAC system
    """
    class Meta:
        model = Group
        interfaces = (relay.Node,)
        fields = '__all__'


class UserType(DjangoObjectType):
    """
    Enhanced User type with comprehensive fields
    """
    # Basic fields
    id = graphene.ID(required=True)
    username = String()
    email = String()
    first_name = String()
    last_name = String()
    full_name = String()
    
    # Profile fields
    phone = String()
    address = String()
    bio = String()
    avatar = String()
    preferences = graphene.JSONString()
    settings = graphene.JSONString()
    
    # Status fields
    is_active = Boolean()
    is_verified = Boolean()
    is_staff = Boolean()
    is_superuser = Boolean()
    date_joined = DateTime()
    last_login = DateTime()
    
    # Computed fields
    orders_count = Field(Int)
    wishlist_count = Field(Int)
    cart_items_count = Field(Int)
    reviews_count = Field(Int)
    
    # Groups and roles
    groups = List(GroupType)
    primary_role = String()
    
    # Permissions
    permissions = List(String)
    
    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'date_joined': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_full_name(self, info):
        """Get user's full name"""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def resolve_orders_count(self, info):
        """Get user's order count"""
        if hasattr(self, 'orders'):
            return self.orders.count()
        return 0

    def resolve_wishlist_count(self, info):
        """Get user's wishlist count"""
        if hasattr(self, 'wishlist_items'):
            return self.wishlist_items.count()
        return 0

    def resolve_cart_items_count(self, info):
        """Get user's cart items count"""
        if hasattr(self, 'cart_items'):
            return self.cart_items.count()
        return 0

    def resolve_reviews_count(self, info):
        """Get user's review count"""
        if hasattr(self, 'reviews'):
            return self.reviews.count()
        return 0

    def resolve_groups(self, info):
        """Get user's groups from auth_group table"""
        return self.groups.all()

    def resolve_primary_role(self, info):
        """Get user's primary role based on groups priority"""
        group_names = [group.name.lower() for group in self.groups.all()]
        
        # Priority order for roles
        role_priority = [
            ('admin', 'Admin'),
            ('administrator', 'Admin'),
            ('vendor', 'Vendor'),
            ('seller', 'Vendor'),
            ('manager', 'Manager'),
            ('moderator', 'Moderator'),
            ('staff', 'Staff'),
            ('customer', 'Customer'),
            ('user', 'User')
        ]
        
        for group_keyword, role_name in role_priority:
            if any(group_keyword in name for name in group_names):
                return role_name
        
        # Fallback to is_staff/is_superuser
        if self.is_superuser:
            return 'Admin'
        elif self.is_staff:
            return 'Staff'
        
        return 'User'

    def resolve_permissions(self, info):
        """Get user's permissions from auth_permission table"""
        if info.context.user.is_authenticated:
            # Returns list like ['api.add_product', 'api.delete_order']
            return list(info.context.user.get_all_permissions())
        return []


class UserProfileType(DjangoObjectType):
    """
    User profile type with extended information
    """
    user = Field(UserType)
    phone = String()
    address = String()
    bio = String()
    avatar = String()
    preferences = graphene.JSONString()
    settings = graphene.JSONString()
    
    # Additional fields
    date_of_birth = graphene.Date()
    gender = String()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = UserProfile
        interfaces = (relay.Node,)
        fields = '__all__'


# Input Types
class UserInput(graphene.InputObjectType):
    """Input for user creation and updates"""
    username = String(required=True)
    email = String(required=True)
    first_name = String()
    last_name = String()
    phone = String()
    address = String()
    bio = String()
    password = String()
    is_active = Boolean(default_value=True)


class UserProfileInput(graphene.InputObjectType):
    """Input for user profile updates"""
    phone = String()
    address = String()
    bio = String()
    avatar = String()
    preferences = graphene.JSONString()
    settings = graphene.JSONString()
    date_of_birth = graphene.Date()
    gender = String()


class UserFilterInput(graphene.InputObjectType):
    """Input for user filtering"""
    username = String()
    email = String()
    is_active = Boolean()
    is_staff = Boolean()
    is_verified = Boolean()
    date_joined_after = DateTime()
    date_joined_before = DateTime()


# Mutations
class CreateUser(Mutation):
    """Create a new user"""
    
    class Arguments:
        input = UserInput(required=True)

    success = Boolean()
    message = String()
    user = Field(UserType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            user = User.objects.create_user(
                username=input.username,
                email=input.email,
                first_name=input.first_name,
                last_name=input.last_name,
                phone=input.phone,
                address=input.address,
                bio=input.bio,
                password=input.password,
                is_active=input.is_active
            )
            
            return CreateUser(
                success=True,
                message="User created successfully",
                user=user
            )
            
        except Exception as e:
            return CreateUser(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateUser(Mutation):
    """Update user information"""
    
    class Arguments:
        id = ID(required=True)
        input = UserInput(required=True)

    success = Boolean()
    message = String()
    user = Field(UserType)
    errors = List(String)

    def mutate(self, info, id, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return UpdateUser(
                success=False,
                message="Authentication required",
                errors=["Authentication required"]
            )
        
        try:
            # Update user fields
            if 'first_name' in input:
                user.first_name = input.first_name
            if 'last_name' in input:
                user.last_name = input.last_name
            if 'phone' in input:
                user.phone = input.phone
            if 'address' in input:
                user.address = input.address
            if 'bio' in input:
                user.bio = input.bio
            
            user.save()
            
            return UpdateUser(
                success=True,
                message="User updated successfully",
                user=user
            )
            
        except Exception as e:
            return UpdateUser(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateUserProfile(Mutation):
    """Update user profile information"""
    
    class Arguments:
        input = UserProfileInput(required=True)

    success = Boolean()
    message = String()
    profile = Field(UserProfileType)
    errors = List(String)

    def mutate(self, info, input):
        user = info.context.user
        
        if not user.is_authenticated:
            return UpdateUserProfile(
                success=False,
                message="Authentication required",
                errors=["Authentication required"]
            )
        
        try:
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update profile fields
            for field, value in input.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            profile.save()
            
            return UpdateUserProfile(
                success=True,
                message="Profile updated successfully",
                profile=profile
            )
            
        except Exception as e:
            return UpdateUserProfile(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateProfile(Mutation):
    """Comprehensive profile update mutation for User and UserProfile"""
    
    class Arguments:
        firstName = String()
        lastName = String()
        email = String()
        phone = String()
        address = String()
        bio = String()
        preferences = graphene.JSONString()

    success = Boolean()
    message = String()
    user = Field(UserType)
    profile = Field(UserProfileType)
    errors = List(String)

    def mutate(self, info, firstName=None, lastName=None, email=None, phone=None, address=None, bio=None, preferences=None):
        user = info.context.user
        
        if not user.is_authenticated:
            return UpdateProfile(
                success=False,
                message="Authentication required",
                errors=["Authentication required"]
            )
        
        try:
            # Update User model fields
            if firstName is not None:
                user.first_name = firstName
            if lastName is not None:
                user.last_name = lastName
            if email is not None:
                user.email = email
            
            user.save()
            
            # Get or create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update UserProfile fields
            if phone is not None:
                profile.phone = phone
            if address is not None:
                profile.address = address
            if bio is not None:
                profile.bio = bio
            if preferences is not None:
                profile.preferences = preferences
            
            profile.save()
            
            return UpdateProfile(
                success=True,
                message="Profile updated successfully",
                user=user,
                profile=profile
            )
            
        except Exception as e:
            return UpdateProfile(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ChangePassword(Mutation):
    """Change user password"""
    
    class Arguments:
        old_password = String(required=True)
        new_password = String(required=True)

    success = Boolean()
    message = String()
    errors = List(String)

    def mutate(self, info, old_password, new_password):
        user = info.context.user
        
        if not user.is_authenticated:
            return ChangePassword(
                success=False,
                message="Authentication required",
                errors=["Authentication required"]
            )
        
        try:
            if not user.check_password(old_password):
                return ChangePassword(
                    success=False,
                    message="Current password is incorrect",
                    errors=["Current password is incorrect"]
                )
            
            user.set_password(new_password)
            user.save()
            
            return ChangePassword(
                success=True,
                message="Password changed successfully"
            )
            
        except Exception as e:
            return ChangePassword(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class DeactivateUser(Mutation):
    """Deactivate user account"""
    
    class Arguments:
        password = String(required=True)

    success = Boolean()
    message = String()
    errors = List(String)

    def mutate(self, info, password):
        user = info.context.user
        
        if not user.is_authenticated:
            return DeactivateUser(
                success=False,
                message="Authentication required",
                errors=["Authentication required"]
            )
        
        try:
            if not user.check_password(password):
                return DeactivateUser(
                    success=False,
                    message="Password is incorrect",
                    errors=["Password is incorrect"]
                )
            
            user.is_active = False
            user.save()
            
            return DeactivateUser(
                success=True,
                message="Account deactivated successfully"
            )
            
        except Exception as e:
            return DeactivateUser(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class UserQuery(ObjectType):
    """User queries"""
    
    me = Field(UserType)
    user = Field(UserType, id=ID(required=True))
    users = List(UserType)
    users_connection = DjangoFilterConnectionField(UserType)
    
    def resolve_me(self, info):
        """Get current authenticated user"""
        user = info.context.user
        if user.is_authenticated:
            return user
        return None

    def resolve_user(self, info, id):
        """Get user by ID"""
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None

    def resolve_users(self, info):
        """Get all users (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return User.objects.all()
        return []


# Mutation Class
class UserMutation(ObjectType):
    """User mutations"""
    
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    update_user_profile = UpdateUserProfile.Field()
    update_profile = UpdateProfile.Field()
    change_password = ChangePassword.Field()
    deactivate_user = DeactivateUser.Field()
