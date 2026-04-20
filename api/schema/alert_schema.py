"""
Enhanced Alert Schema for VynilArt API
"""
import graphene
import json
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, F, Q
from api.models.alert import Alert, AlertRule

User = get_user_model()


class AlertType(DjangoObjectType):
    """Enhanced Alert type with all required fields"""
    
    # Computed fields
    is_critical = Field(Boolean)
    is_urgent = Field(Boolean)
    days_open = Field(Int)
    requires_immediate_attention = Field(Boolean)
    
    class Meta:
        model = Alert
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'alert_type': ['exact'],
            'is_resolved': ['exact'],
            'priority': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_critical(self, info):
        """Check if alert is critical"""
        return self.is_critical

    def resolve_is_urgent(self, info):
        """Check if alert is urgent"""
        return self.is_urgent

    def resolve_days_open(self, info):
        """Calculate days since alert was created"""
        return self.days_open

    def resolve_requires_immediate_attention(self, info):
        """Check if alert requires immediate attention"""
        return self.requires_immediate_attention


class AlertRuleType(DjangoObjectType):
    """Alert Rule type for managing alert rules"""
    
    class Meta:
        model = AlertRule
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'alert_type': ['exact'],
            'is_active': ['exact'],
        }


# Input Types
class AlertInput(graphene.InputObjectType):
    """Input for creating alerts"""
    product_id = Int(required=True)
    alert_type = String(required=True)
    threshold_value = Float(required=True)
    current_value = Float(required=True)
    priority = String(default_value='MEDIUM')
    title = String()
    message = String()
    metadata = JSONString(default_value=dict)


class AlertRuleInput(graphene.InputObjectType):
    """Input for creating/updating alert rules"""
    product_id = Int(required=True)
    alert_type = String(required=True)
    threshold_value = Float(required=True)
    is_active = Boolean(default_value=True)
    notify_admins = Boolean(default_value=True)
    notify_customers = Boolean(default_value=False)
    auto_resolve = Boolean(default_value=False)


# Enhanced Mutations
class CreateAlert(Mutation):
    """Create a new alert"""
    
    class Arguments:
        input = AlertInput(required=True)

    success = Boolean()
    message = String()
    alert = Field(AlertType)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return CreateAlert(
                success=False, 
                message="Admin authentication required"
            )
        
        try:
            with transaction.atomic():
                product = models.Product.objects.get(id=input.product_id)
                
                alert = models.Alert.objects.create(
                    product=product,
                    alert_type=input.alert_type,
                    threshold_value=input.threshold_value,
                    current_value=input.current_value,
                    priority=input.priority,
                    title=input.title,
                    message=input.message,
                    metadata=input.metadata or {}
                )
                
                # Generate title and message if not provided
                if not input.title or not input.message:
                    alert.generate_title_and_message()
                    alert.save()
                
                return CreateAlert(
                    success=True,
                    message="Alert created successfully",
                    alert=alert
                )
                
        except models.Product.DoesNotExist:
            return CreateAlert(
                success=False, 
                message="Product not found"
            )
        except Exception as e:
            return CreateAlert(
                success=False, 
                message=str(e)
            )


class ResolveAlert(Mutation):
    """Mark an alert as resolved"""
    
    class Arguments:
        alert_id = ID(required=True)

    success = Boolean()
    message = String()
    alert = Field(AlertType)

    def mutate(self, info, alert_id):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return ResolveAlert(
                success=False, 
                message="Admin authentication required"
            )
        
        try:
            with transaction.atomic():
                alert = models.Alert.objects.get(id=alert_id)
                alert.resolve(resolved_by_user=user)
                
                return ResolveAlert(
                    success=True,
                    message="Alert resolved successfully",
                    alert=alert
                )
                
        except models.Alert.DoesNotExist:
            return ResolveAlert(
                success=False, 
                message="Alert not found"
            )
        except Exception as e:
            return ResolveAlert(
                success=False, 
                message=str(e)
            )


class CreateAlertRule(Mutation):
    """Create or update alert rule"""
    
    class Arguments:
        input = AlertRuleInput(required=True)

    success = Boolean()
    message = String()
    rule = Field(AlertRuleType)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return CreateAlertRule(
                success=False, 
                message="Admin authentication required"
            )
        
        try:
            with transaction.atomic():
                product = models.Product.objects.get(id=input.product_id)
                
                rule, created = models.AlertRule.objects.get_or_create(
                    product=product,
                    alert_type=input.alert_type,
                    defaults={
                        'threshold_value': input.threshold_value,
                        'is_active': input.is_active,
                        'notify_admins': input.notify_admins,
                        'notify_customers': input.notify_customers,
                        'auto_resolve': input.auto_resolve,
                    }
                )
                
                if not created:
                    # Update existing rule
                    rule.threshold_value = input.threshold_value
                    rule.is_active = input.is_active
                    rule.notify_admins = input.notify_admins
                    rule.notify_customers = input.notify_customers
                    rule.auto_resolve = input.auto_resolve
                    rule.save()
                
                return CreateAlertRule(
                    success=True,
                    message=f"Alert rule {'created' if created else 'updated'} successfully",
                    rule=rule
                )
                
        except models.Product.DoesNotExist:
            return CreateAlertRule(
                success=False, 
                message="Product not found"
            )
        except Exception as e:
            return CreateAlertRule(
                success=False, 
                message=str(e)
            )


class SendAlertNotification(Mutation):
    """Manually send notification for an alert"""
    
    class Arguments:
        alert_id = ID(required=True)

    success = Boolean()
    message = String()
    alert = Field(AlertType)

    def mutate(self, info, alert_id):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return SendAlertNotification(
                success=False, 
                message="Admin authentication required"
            )
        
        try:
            with transaction.atomic():
                alert = models.Alert.objects.get(id=alert_id)
                
                if alert.send_notification():
                    return SendAlertNotification(
                        success=True,
                        message="Notification sent successfully",
                        alert=alert
                    )
                else:
                    return SendAlertNotification(
                        success=False,
                        message="Failed to send notification (already sent or disabled)"
                    )
                
        except models.Alert.DoesNotExist:
            return SendAlertNotification(
                success=False, 
                message="Alert not found"
            )
        except Exception as e:
            return SendAlertNotification(
                success=False, 
                message=str(e)
            )


# Query Class
class AlertQuery(ObjectType):
    """Alert queries"""
    
    alerts = List(AlertType)
    alert = Field(AlertType, id=ID(required=True))
    active_alerts = List(AlertType)
    critical_alerts = List(AlertType)
    alert_rules = List(AlertRuleType)
    alert_summary = Field(JSONString)
    
    def resolve_alerts(self, info):
        """Get all alerts (admin only)"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return []
        
        return models.Alert.objects.all()
    
    def resolve_alert(self, info, id):
        """Get specific alert"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return None
        
        try:
            return models.Alert.objects.get(id=id)
        except models.Alert.DoesNotExist:
            return None
    
    def resolve_active_alerts(self, info):
        """Get active (unresolved) alerts"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return []
        
        return models.Alert.objects.active()
    
    def resolve_critical_alerts(self, info):
        """Get critical alerts"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return []
        
        return models.Alert.objects.filter(
            priority='CRITICAL',
            is_resolved=False
        )
    
    def resolve_alert_rules(self, info):
        """Get alert rules"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return []
        
        return AlertRule.objects.all()
    
    def resolve_alert_summary(self, info):
        """Get alert summary for dashboard"""
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return {}
        
        from api.models.alert import Alert, AlertRule
        
        total_alerts = Alert.objects.count()
        active_alerts = Alert.objects.active().count()
        critical_alerts = Alert.objects.filter(
            priority='CRITICAL',
            is_resolved=False
        ).count()
        
        # Alerts by type
        alerts_by_type = Alert.objects.active().values(
            'alert_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Urgent alerts
        urgent_alerts = Alert.objects.filter(
            is_resolved=False
        ).filter(
            Q(priority='HIGH') | Q(priority='CRITICAL')
        ).count()
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'urgent_alerts': urgent_alerts,
            'alerts_by_type': [
                {
                    'type': item['alert_type'],
                    'count': item['count'],
                    'display': dict(Alert.ALERT_TYPES).get(item['alert_type'], item['alert_type'])
                }
                for item in alerts_by_type
            ],
            'low_stock_products': Alert.objects.low_stock().count(),
            'price_drop_alerts': Alert.objects.price_drop().count(),
            'back_in_stock_alerts': Alert.objects.back_in_stock().count(),
        }


# Mutation Class
class AlertMutation(ObjectType):
    """Alert mutations"""
    
    create_alert = CreateAlert.Field()
    resolve_alert = ResolveAlert.Field()
    create_alert_rule = CreateAlertRule.Field()
    send_alert_notification = SendAlertNotification.Field()
