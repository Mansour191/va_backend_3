"""
Smart Alert Schema for VynilArt API
User-configurable alerts with custom conditions
"""
import graphene
import json
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from api.models.smart_alert import SmartAlert

User = get_user_model()


class SmartAlertType(DjangoObjectType):
    """Smart Alert type with all required fields"""
    
    # Computed fields
    is_enabled = Field(Boolean)
    
    class Meta:
        model = SmartAlert
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'type': ['exact'],
            'is_active': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_enabled(self, info):
        """Check if alert is enabled"""
        return self.is_enabled


# Input Types
class SmartAlertInput(graphene.InputObjectType):
    """Input for creating smart alerts"""
    name = String(required=True)
    type = String(required=True)
    message = String(required=True)
    conditions = JSONString(default_value=dict)
    is_active = Boolean(default_value=True)


class SmartAlertUpdateInput(graphene.InputObjectType):
    """Input for updating smart alerts"""
    name = String()
    message = String()
    conditions = JSONString()
    is_active = Boolean()


# Mutations
class CreateCustomAlert(Mutation):
    """Create a new custom alert with conditions"""
    
    class Arguments:
        input = SmartAlertInput(required=True)

    success = Boolean()
    message = String()
    alert = Field(SmartAlertType)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return CreateCustomAlert(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                alert = SmartAlert.objects.create(
                    user=user,
                    name=input.name,
                    type=input.type,
                    message=input.message,
                    conditions=input.conditions or {},
                    is_active=input.is_active
                )
                
                return CreateCustomAlert(
                    success=True,
                    message="Smart alert created successfully",
                    alert=alert
                )
                
        except Exception as e:
            return CreateCustomAlert(
                success=False, 
                message=str(e)
            )


class ToggleAlertStatus(Mutation):
    """Toggle alert active/inactive status"""
    
    class Arguments:
        alert_id = ID(required=True)

    success = Boolean()
    message = String()
    alert = Field(SmartAlertType)

    def mutate(self, info, alert_id):
        user = info.context.user
        if not user.is_authenticated:
            return ToggleAlertStatus(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                alert = SmartAlert.objects.get(id=alert_id, user=user)
                new_status = alert.toggle_status()
                
                status_text = "enabled" if new_status else "disabled"
                return ToggleAlertStatus(
                    success=True,
                    message=f"Alert {status_text} successfully",
                    alert=alert
                )
                
        except SmartAlert.DoesNotExist:
            return ToggleAlertStatus(
                success=False, 
                message="Alert not found"
            )
        except Exception as e:
            return ToggleAlertStatus(
                success=False, 
                message=str(e)
            )


class UpdateSmartAlert(Mutation):
    """Update an existing smart alert"""
    
    class Arguments:
        alert_id = ID(required=True)
        input = SmartAlertUpdateInput(required=True)

    success = Boolean()
    message = String()
    alert = Field(SmartAlertType)

    def mutate(self, info, alert_id, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateSmartAlert(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                alert = SmartAlert.objects.get(id=alert_id, user=user)
                
                # Update fields if provided
                if input.name is not None:
                    alert.name = input.name
                if input.message is not None:
                    alert.message = input.message
                if input.conditions is not None:
                    alert.conditions = input.conditions
                if input.is_active is not None:
                    alert.is_active = input.is_active
                
                alert.save()
                
                return UpdateSmartAlert(
                    success=True,
                    message="Alert updated successfully",
                    alert=alert
                )
                
        except SmartAlert.DoesNotExist:
            return UpdateSmartAlert(
                success=False, 
                message="Alert not found"
            )
        except Exception as e:
            return UpdateSmartAlert(
                success=False, 
                message=str(e)
            )


class DeleteSmartAlert(Mutation):
    """Delete a smart alert"""
    
    class Arguments:
        alert_id = ID(required=True)

    success = Boolean()
    message = String()

    def mutate(self, info, alert_id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteSmartAlert(
                success=False, 
                message="Authentication required"
            )
        
        try:
            with transaction.atomic():
                alert = SmartAlert.objects.get(id=alert_id, user=user)
                alert.delete()
                
                return DeleteSmartAlert(
                    success=True,
                    message="Alert deleted successfully"
                )
                
        except SmartAlert.DoesNotExist:
            return DeleteSmartAlert(
                success=False, 
                message="Alert not found"
            )
        except Exception as e:
            return DeleteSmartAlert(
                success=False, 
                message=str(e)
            )


# Query Class
class SmartAlertQuery(ObjectType):
    """Smart Alert queries"""
    
    # User-specific queries
    active_alerts = List(SmartAlertType)
    my_alerts = List(SmartAlertType)
    alert = Field(SmartAlertType, id=ID(required=True))
    
    # Admin queries (if needed in future)
    all_alerts = List(SmartAlertType)
    alert_summary = Field(JSONString)
    
    def resolve_active_alerts(self, info):
        """Get active alerts for current user"""
        if not info.context.user.is_authenticated:
            return []
        
        return SmartAlert.objects.active_for_user(info.context.user)
    
    def resolve_my_alerts(self, info):
        """Get all alerts for current user"""
        if not info.context.user.is_authenticated:
            return []
        
        return SmartAlert.objects.for_user(info.context.user)
    
    def resolve_alert(self, info, id):
        """Get specific alert for current user"""
        if not info.context.user.is_authenticated:
            return None
        
        try:
            return SmartAlert.objects.get(id=id, user=info.context.user)
        except SmartAlert.DoesNotExist:
            return None
    
    def resolve_all_alerts(self, info):
        """Get all alerts (admin only)"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return []
        
        return SmartAlert.objects.all()
    
    def resolve_alert_summary(self, info):
        """Get alert summary for dashboard"""
        if not info.context.user.is_authenticated:
            return {}
        
        user = info.context.user
        
        # User summary
        if not user.is_staff:
            total_alerts = SmartAlert.objects.for_user(user).count()
            active_alerts = SmartAlert.objects.active_for_user(user).count()
            
            # Alerts by type
            alerts_by_type = SmartAlert.objects.for_user(user).values(
                'type'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'alerts_by_type': [
                    {
                        'type': item['type'],
                        'count': item['count'],
                        'display': dict(SmartAlert.ALERT_TYPES).get(item['type'], item['type'])
                    }
                    for item in alerts_by_type
                ],
            }
        
        # Admin summary
        total_alerts = SmartAlert.objects.count()
        active_alerts = SmartAlert.objects.active().count()
        total_users = SmartAlert.objects.values('user').distinct().count()
        
        # Alerts by type
        alerts_by_type = SmartAlert.objects.values(
            'type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Most active users
        most_active_users = SmartAlert.objects.values(
            'user__username'
        ).annotate(
            alert_count=Count('id')
        ).order_by('-alert_count')[:10]
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'total_users': total_users,
            'alerts_by_type': [
                {
                    'type': item['type'],
                    'count': item['count'],
                    'display': dict(SmartAlert.ALERT_TYPES).get(item['type'], item['type'])
                }
                for item in alerts_by_type
            ],
            'most_active_users': list(most_active_users),
        }


# Mutation Class
class SmartAlertMutation(ObjectType):
    """Smart Alert mutations"""
    
    create_custom_alert = CreateCustomAlert.Field()
    toggle_alert_status = ToggleAlertStatus.Field()
    update_smart_alert = UpdateSmartAlert.Field()
    delete_smart_alert = DeleteSmartAlert.Field()


# Export for use in main schema
__all__ = [
    'SmartAlertType',
    'SmartAlertQuery', 
    'SmartAlertMutation',
    'CreateCustomAlert',
    'ToggleAlertStatus',
    'UpdateSmartAlert',
    'DeleteSmartAlert'
]
