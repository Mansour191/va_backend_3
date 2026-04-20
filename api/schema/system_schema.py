"""
System Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg
from django.utils import timezone
from api.models.notification import Notification
from api.models.erpnext import ERPNextSyncLog
from api.models.conversation import ConversationHistory
from api.models.dashboard import DashboardSettings
from api.models.system import SystemConfiguration
from api.schema.user_schema import UserType


class NotificationType(DjangoObjectType):
    """Enhanced notification type"""
    id = graphene.ID(required=True)
    user = Field(lambda: UserType)
    title = String()
    message = String()
    type = String()
    
    # Enhanced fields
    sender = String()
    recipient_type = String()
    recipient_group = String()
    recipient_segment = String()
    priority = String()
    category = String()
    
    # Metadata and technical fields
    metadata = JSONString()
    action_url = String()
    action_text = String()
    action_button_color = String()
    
    # Status and timing
    is_read = Boolean()
    is_archived = Boolean()
    is_starred = Boolean()
    read_at = DateTime()
    expires_at = DateTime()
    
    # Additional data
    data = JSONString()
    
    # Delivery tracking
    delivery_channels = List(String)
    delivery_status = JSONString()
    
    # Computed fields
    is_expired = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Notification
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'type': ['exact'],
            'is_read': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_expired(self, info):
        """Check if notification is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ERPNextSyncLogType(DjangoObjectType):
    """ERPNext synchronization log type"""
    id = graphene.ID(required=True)
    sync_id = String()
    action = String()
    entity_type = String()
    
    # Status and progress
    status = String()
    progress_percentage = Int()
    
    # Statistics
    records_total = Int()
    records_synced = Int()
    records_failed = Int()
    records_skipped = Int()
    
    # Timing information
    started_at = DateTime()
    completed_at = DateTime()
    duration_seconds = Int()
    
    # Error handling
    error_message = String()
    error_details = JSONString()
    retry_count = Int()
    max_retries = Int()
    
    # Data and metadata
    sync_data = JSONString()
    response_data = JSONString()
    
    # Performance metrics
    api_calls_count = Int()
    data_size_bytes = Int()
    average_response_time = Float()
    
    # User and system context
    triggered_by = Field(lambda: UserType)
    system_version = String()
    api_version = String()

    class Meta:
        model = ERPNextSyncLog
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'sync_id': ['exact'],
            'entity_type': ['exact'],
            'status': ['exact'],
            'triggered_by': ['exact'],
            'started_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_can_retry(self, info):
        """Check if sync can be retried"""
        return self.retry_count < self.max_retries and self.status == 'failed'


class SystemConfigurationType(DjangoObjectType):
    """System configuration type"""
    id = graphene.ID(required=True)
    key = String()
    value = String()
    config_type = String()
    
    # Validation and constraints
    data_type = String()
    is_required = Boolean()
    default_value = String()
    
    # Validation rules
    min_value = Float()
    max_value = Float()
    allowed_values = List(String)
    validation_regex = String()
    
    # Access control
    is_public = Boolean()
    is_editable = Boolean()
    requires_restart = Boolean()
    
    # Organization and environment
    # organization = Field(lambda: OrganizationType)  # OrganizationType not defined
    environment = String()
    
    # Audit trail
    created_by = Field(lambda: UserType)
    updated_by = Field(lambda: UserType)
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = SystemConfiguration
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'key': ['exact'],
            'config_type': ['exact'],
            'organization': ['exact'],
            'environment': ['exact'],
            'is_public': ['exact'],
            'is_editable': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def get_typed_value(self):
        """Get value in correct data type"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.data_type == 'json':
            return json.loads(self.value)
        else:
            return self.value


# Input Types
class NotificationInput(graphene.InputObjectType):
    """Input for notification creation"""
    user_id = ID()
    title = String(required=True)
    message = String(required=True)
    type = String(required=True)
    
    # Enhanced fields
    sender = String()
    recipient_type = String()
    recipient_group = String()
    recipient_segment = String()
    priority = String()
    category = String()
    
    # Metadata and technical fields
    metadata = JSONString()
    action_url = String()
    action_text = String()
    action_button_color = String()
    
    # Status and timing
    expires_at = DateTime()
    
    # Additional data
    data = JSONString()


class SystemConfigurationInput(graphene.InputObjectType):
    """Input for system configuration"""
    key = String(required=True)
    value = String(required=True)
    config_type = String(required=True)
    
    # Validation and constraints
    data_type = String()
    is_required = Boolean()
    default_value = String()
    
    # Validation rules
    min_value = Float()
    max_value = Float()
    allowed_values = List(String)
    validation_regex = String()
    
    # Access control
    is_public = Boolean(default_value=False)
    is_editable = Boolean(default_value=True)
    requires_restart = Boolean(default_value=False)
    
    # Organization and environment
    organization_id = ID()
    environment = String()


# Mutations
class CreateNotification(Mutation):
    """Create a new notification"""
    
    class Arguments:
        input = NotificationInput(required=True)

    success = Boolean()
    message = String()
    notification = Field(NotificationType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.system import Notification
            from api.models.user import User
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateNotification(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            # Handle user
            target_user = None
            if 'user_id' in input:
                target_user = User.objects.get(id=input['user_id'])
            
            notification = Notification.objects.create(
                user=target_user,
                **{k: v for k, v in input.items() if k != 'user_id'}
            )
            
            return CreateNotification(
                success=True,
                message="Notification created successfully",
                notification=notification
            )
            
        except Exception as e:
            return CreateNotification(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class MarkNotificationAsRead(Mutation):
    """Mark notification as read"""
    
    class Arguments:
        notification_id = ID(required=True)

    success = Boolean()
    message = String()
    notification = Field(NotificationType)
    errors = List(String)

    def mutate(self, info, notification_id):
        try:
            from api.models.system import Notification
            
            user = info.context.user
            
            if not user.is_authenticated:
                return MarkNotificationAsRead(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            notification = Notification.objects.get(id=notification_id)
            
            # Check ownership
            if notification.user != user:
                return MarkNotificationAsRead(
                    success=False,
                    message="Access denied",
                    errors=["Access denied"]
                )
            
            notification.mark_as_read()
            
            return MarkNotificationAsRead(
                success=True,
                message="Notification marked as read",
                notification=notification
            )
            
        except Notification.DoesNotExist:
            return MarkNotificationAsRead(
                success=False,
                message="Notification not found",
                errors=["Notification not found"]
            )
        except Exception as e:
            return MarkNotificationAsRead(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ArchiveNotification(Mutation):
    """Archive notification"""
    
    class Arguments:
        notification_id = ID(required=True)

    success = Boolean()
    message = String()
    notification = Field(NotificationType)
    errors = List(String)

    def mutate(self, info, notification_id):
        try:
            from api.models.system import Notification
            
            user = info.context.user
            
            if not user.is_authenticated:
                return ArchiveNotification(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            notification = Notification.objects.get(id=notification_id)
            
            # Check ownership
            if notification.user != user:
                return ArchiveNotification(
                    success=False,
                    message="Access denied",
                    errors=["Access denied"]
                )
            
            notification.archive()
            
            return ArchiveNotification(
                success=True,
                message="Notification archived",
                notification=notification
            )
            
        except Notification.DoesNotExist:
            return ArchiveNotification(
                success=False,
                message="Notification not found",
                errors=["Notification not found"]
            )
        except Exception as e:
            return ArchiveNotification(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateSystemConfiguration(Mutation):
    """Create a new system configuration"""
    
    class Arguments:
        input = SystemConfigurationInput(required=True)

    success = Boolean()
    message = String()
    configuration = Field(SystemConfigurationType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.system import SystemConfiguration
            from api.models.organization import Organization
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateSystemConfiguration(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            # Handle organization
            organization = None
            if 'organization_id' in input:
                organization = Organization.objects.get(id=input['organization_id'])
            
            configuration = SystemConfiguration.objects.create(
                created_by=user,
                organization=organization,
                **{k: v for k, v in input.items() if k != 'organization_id'}
            )
            
            return CreateSystemConfiguration(
                success=True,
                message="System configuration created successfully",
                configuration=configuration
            )
            
        except Exception as e:
            return CreateSystemConfiguration(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateSystemConfiguration(Mutation):
    """Update an existing system configuration"""
    
    class Arguments:
        id = ID(required=True)
        input = SystemConfigurationInput(required=True)

    success = Boolean()
    message = String()
    configuration = Field(SystemConfigurationType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            from api.models.system import SystemConfiguration
            from api.models.organization import Organization
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return UpdateSystemConfiguration(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            configuration = SystemConfiguration.objects.get(id=id)
            
            # Handle organization
            if 'organization_id' in input:
                configuration.organization = Organization.objects.get(id=input['organization_id'])
            
            # Update fields
            for field, value in input.items():
                if field != 'organization_id' and hasattr(configuration, field):
                    setattr(configuration, field, value)
            
            configuration.updated_by = user
            configuration.save()
            
            return UpdateSystemConfiguration(
                success=True,
                message="System configuration updated successfully",
                configuration=configuration
            )
            
        except SystemConfiguration.DoesNotExist:
            return UpdateSystemConfiguration(
                success=False,
                message="Configuration not found",
                errors=["Configuration not found"]
            )
        except Exception as e:
            return UpdateSystemConfiguration(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class SystemQuery(ObjectType):
    """System queries"""
    
    # Notification queries
    notifications = List(NotificationType)
    notification = Field(NotificationType, id=ID(required=True))
    my_notifications = List(NotificationType)
    unread_notifications = List(NotificationType)
    
    # ERPNext sync queries
    erp_sync_logs = List(ERPNextSyncLogType)
    erp_sync_log = Field(ERPNextSyncLogType, id=ID(required=True))
    
    # System configuration queries
    system_configurations = List(SystemConfigurationType)
    system_configuration = Field(SystemConfigurationType, key=String(required=True))
    public_configurations = List(SystemConfigurationType)
    
    def resolve_notifications(self, info):
        """Get all notifications (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Notification.objects.all()
        return []
    
    def resolve_notification(self, info, id):
        """Get notification by ID"""
        user = info.context.user
        try:
            notification = Notification.objects.get(id=id)
            # Check ownership or admin
            if user.is_authenticated and (
                user.is_staff or 
                notification.user == user
            ):
                return notification
            return None
        except Notification.DoesNotExist:
            return None
    
    def resolve_my_notifications(self, info):
        """Get current user's notifications"""
        user = info.context.user
        if user.is_authenticated:
            return Notification.objects.filter(user=user)
        return []
    
    def resolve_unread_notifications(self, info):
        """Get current user's unread notifications"""
        user = info.context.user
        if user.is_authenticated:
            return Notification.objects.filter(user=user, is_read=False)
        return []
    
    def resolve_erp_sync_logs(self, info):
        """Get all ERP sync logs (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ERPNextSyncLog.objects.all()
        return []
    
    def resolve_erp_sync_log(self, info, id):
        """Get ERP sync log by ID"""
        user = info.context.user
        try:
            log = ERPNextSyncLog.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return log
            return None
        except ERPNextSyncLog.DoesNotExist:
            return None
    
    def resolve_system_configurations(self, info):
        """Get all system configurations (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return SystemConfiguration.objects.all()
        return []
    
    def resolve_system_configuration(self, info, key):
        """Get system configuration by key"""
        user = info.context.user
        try:
            config = SystemConfiguration.objects.get(key=key)
            # Check access
            if user.is_authenticated and (
                user.is_staff or 
                config.is_public
            ):
                return config
            return None
        except SystemConfiguration.DoesNotExist:
            return None
    
    def resolve_public_configurations(self, info):
        """Get public system configurations"""
        return SystemConfiguration.objects.filter(is_public=True)


# Mutation Class
class SystemMutation(ObjectType):
    """System mutations"""
    
    create_notification = CreateNotification.Field()
    mark_notification_as_read = MarkNotificationAsRead.Field()
    archive_notification = ArchiveNotification.Field()
    create_system_configuration = CreateSystemConfiguration.Field()
    update_system_configuration = UpdateSystemConfiguration.Field()
