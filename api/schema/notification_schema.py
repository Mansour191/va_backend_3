"""
Notification Schema for VynilArt API
Contains GraphQL types, queries, and mutations for Notification Management
"""
import graphene
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Boolean, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.db.models import F, Q
from ..models import Notification, Alert

User = get_user_model()


class NotificationType(DjangoObjectType):
    """
    GraphQL type for Notification model
    """
    data_json = JSONString()
    unread_count = Int()
    
    class Meta:
        model = Notification
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'is_read': ['exact'],
        }
    
    def resolve_data_json(self, info):
        """
        Resolve data as JSON string for easier frontend handling
        """
        if self.data:
            return self.data
        return {}
    
    def resolve_unread_count(self, info):
        """
        Resolve unread count for the current user
        """
        if hasattr(info.context, 'user') and info.context.user.is_authenticated:
            return Notification.objects.filter(
                user=info.context.user,
                is_read=False
            ).count()
        return 0


class AlertType(DjangoObjectType):
    """
    GraphQL type for Alert model
    """
    conditions_json = JSONString()
    
    class Meta:
        model = Alert
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'id': ['exact'],
        }
    
    def resolve_conditions_json(self, info):
        """
        Resolve conditions as JSON string
        """
        if self.conditions:
            return self.conditions
        return {}


class MarkNotificationAsRead(Mutation):
    """
    Mutation to mark a notification as read
    """
    class Arguments:
        id = ID(required=True, description="Notification ID to mark as read")
        mark_all = Boolean(default_value=False, description="Mark all notifications as read")
    
    success = Boolean()
    notification = Field(NotificationType)
    unread_count = Int()
    
    def mutate(self, info, id=None, mark_all=False):
        """
        Mark notification(s) as read
        """
        if not info.context.user.is_authenticated:
            raise Exception("Authentication required")
        
        user = info.context.user
        
        if mark_all:
            # Mark all notifications as read for the user
            updated_count = Notification.objects.filter(
                user=user,
                is_read=False
            ).update(is_read=True)
            
            # Get unread count after update
            unread_count = Notification.objects.filter(
                user=user,
                is_read=False
            ).count()
            
            return MarkNotificationAsRead(
                success=True,
                unread_count=unread_count
            )
        
        elif id:
            try:
                notification = Notification.objects.get(id=id, user=user)
                notification.is_read = True
                notification.save()
                
                # Get unread count after update
                unread_count = Notification.objects.filter(
                    user=user,
                    is_read=False
                ).count()
                
                return MarkNotificationAsRead(
                    success=True,
                    notification=notification,
                    unread_count=unread_count
                )
            except Notification.DoesNotExist:
                raise Exception("Notification not found")
        
        return MarkNotificationAsRead(success=False)


class DeleteNotification(Mutation):
    """
    Mutation to delete a notification
    """
    class Arguments:
        id = ID(required=True, description="Notification ID to delete")
    
    success = Boolean()
    unread_count = Int()
    
    def mutate(self, info, id):
        """
        Delete a notification
        """
        if not info.context.user.is_authenticated:
            raise Exception("Authentication required")
        
        try:
            notification = Notification.objects.get(id=id, user=info.context.user)
            notification.delete()
            
            # Get unread count after deletion
            unread_count = Notification.objects.filter(
                user=info.context.user,
                is_read=False
            ).count()
            
            return DeleteNotification(
                success=True,
                unread_count=unread_count
            )
        except Notification.DoesNotExist:
            raise Exception("Notification not found")


class CreateNotification(Mutation):
    """
    Mutation to create a new notification (admin/staff only)
    """
    class Arguments:
        user_id = ID(required=True, description="User ID to send notification to")
        title = String(required=True)
        message = String(required=True)
        type = String(default_value='info')
        data = JSONString(default_value='{}')
    
    notification = Field(NotificationType)
    success = Boolean()
    
    def mutate(self, info, user_id, **kwargs):
        """
        Create a new notification
        """
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            raise Exception("Admin access required")
        
        try:
            user = User.objects.get(id=user_id)
            data = kwargs.pop('data', {})
            
            notification = Notification.objects.create(
                user=user,
                data=data,
                **kwargs
            )
            
            return CreateNotification(
                notification=notification,
                success=True
            )
        except User.DoesNotExist:
            raise Exception("User not found")


class NotificationQuery(ObjectType):
    """
    Notification-related queries
    """
    notifications = DjangoFilterConnectionField(NotificationType)
    notification = Field(NotificationType, id=ID(required=True))
    unread_notifications = List(NotificationType)
    unread_count = Int()
    
    def resolve_unread_notifications(self, info):
        """
        Get unread notifications for the current user
        """
        if not info.context.user.is_authenticated:
            return []
        
        return Notification.objects.filter(
            user=info.context.user,
            is_read=False
        ).order_by('-created_at')[:20]  # Limit to 20 most recent
    
    def resolve_unread_count(self, info):
        """
        Get unread notifications count for the current user
        """
        if not info.context.user.is_authenticated:
            return 0
        
        return Notification.objects.filter(
            user=info.context.user,
            is_read=False
        ).count()


class NotificationMutation(ObjectType):
    """
    Notification-related mutations
    """
    mark_notification_as_read = MarkNotificationAsRead.Field()
    delete_notification = DeleteNotification.Field()
    create_notification = CreateNotification.Field()
