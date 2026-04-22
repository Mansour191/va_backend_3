"""
GraphQL Authentication and Authorization Middleware
"""
import jwt
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.conf import settings
from graphql.error import GraphQLError
from graphene_django.views import GraphQLView
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthMiddleware:
    """
    Middleware to handle JWT authentication in GraphQL requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for non-GraphQL requests
        if not request.path.startswith('/graphql/'):
            return self.get_response(request)
        
        # Extract JWT token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            try:
                # Decode JWT token
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                
                # Get user from token
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id, is_active=True)
                        request.user = user
                    except User.DoesNotExist:
                        request.user = AnonymousUser()
                else:
                    request.user = AnonymousUser()
                    
            except jwt.ExpiredSignatureError:
                logger.warning("JWT token has expired")
                request.user = AnonymousUser()
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid JWT token: {e}")
                request.user = AnonymousUser()
            except Exception as e:
                logger.error(f"JWT authentication error: {e}")
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        return self.get_response(request)


class AuthenticatedGraphQLView(GraphQLView):
    """
    Custom GraphQL View with enhanced authentication and error handling
    """
    
    def execute_graphql_request(self, request, data, query, variables, operation_name, show_graphiql=False):
        """
        Override to add authentication checks and enhanced error handling
        """
        # Add user context to GraphQL execution
        if hasattr(request, 'user'):
            # Create context with user and additional info
            context = {
                'user': request.user,
                'request': request,
                'is_authenticated': request.user.is_authenticated,
                'is_staff': request.user.is_staff if request.user.is_authenticated else False,
            }
        else:
            context = {
                'user': AnonymousUser(),
                'request': request,
                'is_authenticated': False,
                'is_staff': False,
            }
        
        # Log GraphQL requests for debugging
        logger.info(f"GraphQL Request - User: {context['user']}, Query: {query[:100]}...")
        
        try:
            result = super().execute_graphql_request(
                request, data, query, variables, operation_name, show_graphiql
            )
            
            # Add context to result if needed
            if hasattr(result, 'context'):
                result.context.update(context)
                
            return result
            
        except Exception as e:
            logger.error(f"GraphQL execution error: {e}")
            # Return a proper GraphQL error
            from graphql.error import GraphQLError
            return GraphQLError(str(e), extensions={'code': 'INTERNAL_ERROR'})


def check_permission(user, permission_required):
    """
    Helper function to check if user has required permission
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Check specific permission
    if user.has_perm(permission_required):
        return True
    
    return False


def check_group_membership(user, group_name):
    """
    Helper function to check if user belongs to a specific group
    """
    if not user.is_authenticated:
        return False
    
    return user.groups.filter(name=group_name).exists()


class PermissionRequiredMixin:
    """
    Mixin for GraphQL resolvers that require specific permissions
    """
    
    permission_required = None
    group_required = None
    
    @classmethod
    def has_permission(cls, info):
        """
        Check if the current user has the required permissions
        """
        user = info.context.user
        
        if not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        # Check specific permission
        if cls.permission_required:
            if not user.has_perm(cls.permission_required):
                return False
        
        # Check group membership
        if cls.group_required:
            if not user.groups.filter(name=cls.group_required).exists():
                return False
        
        return True


class StaffRequiredMixin:
    """
    Mixin for GraphQL resolvers that require staff privileges
    """
    
    @classmethod
    def has_permission(cls, info):
        """
        Check if the current user is staff
        """
        user = info.context.user
        return user.is_authenticated and (user.is_staff or user.is_superuser)


class InvestorRequiredMixin:
    """
    Mixin for GraphQL resolvers that require investor privileges
    """
    
    @classmethod
    def has_permission(cls, info):
        """
        Check if the current user is an investor
        """
        user = info.context.user
        
        if not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        # Check if user belongs to investors group
        return user.groups.filter(name__in=['investors', 'admin']).exists()


# Custom GraphQL Errors
class AuthenticationError(GraphQLError):
    """
    Custom GraphQL error for authentication failures
    """
    def __init__(self, message="Authentication required"):
        super().__init__(message, extensions={'code': 'AUTHENTICATION_ERROR'})


class PermissionError(GraphQLError):
    """
    Custom GraphQL error for permission failures
    """
    def __init__(self, message="Permission denied"):
        super().__init__(message, extensions={'code': 'PERMISSION_ERROR'})


class ValidationError(GraphQLError):
    """
    Custom GraphQL error for validation failures
    """
    def __init__(self, message, field=None):
        extensions = {'code': 'VALIDATION_ERROR'}
        if field:
            extensions['field'] = field
        super().__init__(message, extensions=extensions)


# Utility functions for JWT
def generate_jwt_token(user):
    """
    Generate JWT token for authenticated user
    """
    import datetime
    
    payload = {
        'user_id': str(user.id),  # Convert UUID to string
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 7 days expiry
        'iat': datetime.datetime.utcnow(),
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def verify_jwt_token(token):
    """
    Verify and decode JWT token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


# Context processor for GraphQL
def get_graphql_context(request):
    """
    Create context for GraphQL execution
    """
    return {
        'user': getattr(request, 'user', AnonymousUser()),
        'request': request,
        'is_authenticated': getattr(request, 'user', AnonymousUser()).is_authenticated,
        'is_staff': getattr(request, 'user', AnonymousUser()).is_staff,
    }
