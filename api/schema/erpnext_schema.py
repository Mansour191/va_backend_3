"""
ERPNext Integration Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg

from api.models.erpnext import ERPNextSyncLog


class ERPNextSyncLogType(DjangoObjectType):
    """ERPNext sync log type"""
    id = graphene.ID(required=True)
    model_name = String()
    record_id = String()
    action = String()
    status = String()
    request_data = JSONString()
    response_data = JSONString()
    error_message = String()
    sync_timestamp = DateTime()
    retry_count = Int()
    last_retry_at = DateTime()
    
    # Computed fields
    is_success = Boolean()
    duration = Float()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = ERPNextSyncLog
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'model_name': ['exact', 'icontains'],
            'action': ['exact'],
            'status': ['exact'],
            'sync_timestamp': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_success(self, info):
        """Check if sync was successful"""
        return self.status == 'success'

    def resolve_duration(self, info):
        """Calculate sync duration in seconds"""
        if self.sync_timestamp:
            from django.utils import timezone
            return (timezone.now() - self.sync_timestamp).total_seconds()
        return None


# Input Types
class ERPNextSyncLogInput(graphene.InputObjectType):
    """Input for ERPNext sync log creation"""
    model_name = String(required=True)
    record_id = String(required=True)
    action = String(required=True)
    status = String(required=True)
    request_data = JSONString()
    response_data = JSONString()
    error_message = String()


# Mutations
class CreateERPNextSyncLog(Mutation):
    """Create a new ERPNext sync log"""
    
    class Arguments:
        input = ERPNextSyncLogInput(required=True)

    success = Boolean()
    message = String()
    sync_log = Field(ERPNextSyncLogType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            sync_log = ERPNextSyncLog.objects.create(**input)
            
            return CreateERPNextSyncLog(
                success=True,
                message="ERPNext sync log created successfully",
                sync_log=sync_log
            )
            
        except Exception as e:
            return CreateERPNextSyncLog(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class RetryERPNextSync(Mutation):
    """Retry failed ERPNext sync"""
    
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()
    sync_log = Field(ERPNextSyncLogType)
    errors = List(String)

    def mutate(self, info, id):
        try:
            sync_log = ERPNextSyncLog.objects.get(id=id)
            
            if sync_log.status == 'success':
                return RetryERPNextSync(
                    success=False,
                    message="Sync already successful",
                    errors=["Sync already successful"]
                )
            
            # Increment retry count and update timestamp
            sync_log.retry_count += 1
            sync_log.last_retry_at = timezone.now()
            sync_log.save()
            
            # Here you would implement actual retry logic
            # For now, just update the log
            
            return RetryERPNextSync(
                success=True,
                message="ERPNext sync retry initiated",
                sync_log=sync_log
            )
            
        except ERPNextSyncLog.DoesNotExist:
            return RetryERPNextSync(
                success=False,
                message="ERPNext sync log not found",
                errors=["ERPNext sync log not found"]
            )
        except Exception as e:
            return RetryERPNextSync(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class ERPNextQuery(ObjectType):
    """ERPNext queries"""
    
    erpnext_sync_logs = List(ERPNextSyncLogType)
    erpnext_sync_log = Field(ERPNextSyncLogType, id=ID(required=True))
    failed_sync_logs = List(ERPNextSyncLogType)
    sync_logs_by_model = List(ERPNextSyncLogType, model_name=String(required=True))
    
    def resolve_erpnext_sync_logs(self, info):
        """Get all ERPNext sync logs"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ERPNextSyncLog.objects.all().order_by('-sync_timestamp')
        return []
    
    def resolve_erpnext_sync_log(self, info, id):
        """Get ERPNext sync log by ID"""
        user = info.context.user
        try:
            sync_log = ERPNextSyncLog.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return sync_log
            return None
        except ERPNextSyncLog.DoesNotExist:
            return None
    
    def resolve_failed_sync_logs(self, info):
        """Get failed ERPNext sync logs"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ERPNextSyncLog.objects.filter(status='failed').order_by('-sync_timestamp')
        return []
    
    def resolve_sync_logs_by_model(self, info, model_name):
        """Get sync logs for specific model"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return ERPNextSyncLog.objects.filter(model_name=model_name).order_by('-sync_timestamp')
        return []


# Mutation Class
class ERPNextMutation(ObjectType):
    """ERPNext mutations"""
    
    create_erpnext_sync_log = CreateERPNextSyncLog.Field()
    retry_erpnext_sync = RetryERPNextSync.Field()
