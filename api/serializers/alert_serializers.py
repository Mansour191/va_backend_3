"""
Alert Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.alert import Alert, AlertRule


class AlertRuleSerializer(serializers.ModelSerializer):
    """Alert rule serializer"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'product', 'product_name', 'alert_type',
            'threshold_value', 'comparison_operator',
            'notification_settings', 'is_active', 'priority',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertSerializer(serializers.ModelSerializer):
    """Alert serializer"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_resolved = serializers.SerializerMethodField()
    time_until_resolution = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'product', 'product_name', 'user', 'user_name',
            'alert_type', 'threshold_value', 'current_value',
            'priority', 'title', 'message', 'metadata',
            'is_resolved', 'is_notification_sent',
            'is_email_sent', 'is_sms_sent', 'is_push_sent',
            'resolved_at', 'created_at', 'updated_at',
            'time_until_resolution'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_resolved(self, obj):
        """Check if alert is resolved"""
        return obj.is_resolved
    
    def get_time_until_resolution(self, obj):
        """Calculate time until resolution"""
        if obj.is_resolved:
            return None
        
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return {
            'hours': delta.total_seconds() / 3600,
            'days': delta.days
        }


class AlertRuleCreateSerializer(serializers.ModelSerializer):
    """Alert rule creation serializer"""
    class Meta:
        model = AlertRule
        fields = [
            'product', 'alert_type', 'threshold_value',
            'comparison_operator', 'notification_settings',
            'is_active', 'priority', 'description'
        ]
    
    def validate_threshold_value(self, value):
        """Validate threshold value"""
        if value <= 0:
            raise serializers.ValidationError(
                "Threshold value must be greater than 0"
            )
        return value
    
    def validate(self, data):
        """Validate alert rule"""
        product = data.get('product')
        alert_type = data.get('alert_type')
        
        # Check for duplicate rules
        if AlertRule.objects.filter(
            product=product,
            alert_type=alert_type,
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "An active alert rule for this product and type already exists"
            )
        
        return data
    
    def create(self, validated_data):
        """Create alert rule"""
        return AlertRule.objects.create(**validated_data)


class AlertCreateSerializer(serializers.ModelSerializer):
    """Alert creation serializer"""
    class Meta:
        model = Alert
        fields = [
            'product', 'user', 'alert_type', 'threshold_value',
            'current_value', 'priority', 'title', 'message',
            'metadata', 'is_notification_sent', 'is_email_sent',
            'is_sms_sent', 'is_push_sent'
        ]
    
    def validate(self, data):
        """Validate alert data"""
        if not data.get('user') and data.get('alert_type') in ['stock_low', 'price_drop']:
            # System alerts don't need user
            pass
        elif data.get('alert_type') == 'custom' and not data.get('user'):
            raise serializers.ValidationError(
                "User is required for custom alerts"
            )
        
        return data
    
    def create(self, validated_data):
        """Create alert"""
        return Alert.objects.create(**validated_data)


class AlertResolveSerializer(serializers.Serializer):
    """Alert resolution serializer"""
    alert_id = serializers.IntegerField(required=True)
    resolution_note = serializers.CharField(required=False)
    notify_user = serializers.BooleanField(default=True)
    
    def validate_alert_id(self, value):
        """Validate alert exists"""
        if not Alert.objects.filter(id=value).exists():
            raise serializers.ValidationError("Alert not found")
        return value
    
    def save(self):
        """Resolve alert"""
        alert_id = self.validated_data['alert_id']
        resolution_note = self.validated_data.get('resolution_note', '')
        notify_user = self.validated_data['notify_user']
        
        try:
            alert = Alert.objects.get(id=alert_id)
            alert.resolve(resolution_note, notify_user)
            return {
                'status': 'success',
                'alert': alert,
                'message': 'Alert resolved successfully'
            }
        except Alert.DoesNotExist:
            return {
                'status': 'error',
                'message': 'Alert not found'
            }


class AlertBulkActionSerializer(serializers.Serializer):
    """Alert bulk action serializer"""
    action = serializers.ChoiceField(
        choices=['resolve_all', 'delete_resolved', 'send_notifications'],
        required=True
    )
    alert_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    filters = serializers.DictField(required=False)
    
    def validate(self, data):
        """Validate bulk action data"""
        action = data['action']
        
        if action in ['resolve_all', 'delete_resolved'] and not data.get('alert_ids'):
            raise serializers.ValidationError(
                "alert_ids required for resolve_all/delete_resolved actions"
            )
        
        return data
    
    def save(self):
        """Execute bulk action"""
        action = self.validated_data['action']
        
        if action == 'resolve_all':
            # Resolve multiple alerts
            alert_ids = self.validated_data['alert_ids']
            alerts = Alert.objects.filter(id__in=alert_ids)
            
            for alert in alerts:
                alert.resolve("Bulk resolution", True)
            
            return {
                'status': 'success',
                'resolved_count': alerts.count(),
                'message': f'{alerts.count()} alerts resolved'
            }
        
        elif action == 'delete_resolved':
            # Delete resolved alerts
            Alert.objects.filter(is_resolved=True).delete()
            
            return {
                'status': 'success',
                'message': 'All resolved alerts deleted'
            }
        
        elif action == 'send_notifications':
            # Send notifications for active alerts
            filters = self.validated_data.get('filters', {})
            alerts = Alert.objects.filter(is_resolved=False, **filters)
            
            for alert in alerts:
                alert.send_notification()
            
            return {
                'status': 'success',
                'notification_count': alerts.count(),
                'message': f'Notifications sent for {alerts.count()} alerts'
            }


class AlertStatisticsSerializer(serializers.Serializer):
    """Alert statistics serializer"""
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    alert_type = serializers.CharField(required=False)
    priority = serializers.CharField(required=False)
    
    def validate(self, data):
        """Validate date range"""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "date_from must be before date_to"
            )
        
        return data
    
    def save(self):
        """Get alert statistics"""
        filters = {}
        
        if self.validated_data.get('date_from'):
            filters['created_at__gte'] = self.validated_data['date_from']
        
        if self.validated_data.get('date_to'):
            filters['created_at__lte'] = self.validated_data['date_to']
        
        if self.validated_data.get('alert_type'):
            filters['alert_type'] = self.validated_data['alert_type']
        
        if self.validated_data.get('priority'):
            filters['priority'] = self.validated_data['priority']
        
        alerts = Alert.objects.filter(**filters)
        
        return {
            'total_alerts': alerts.count(),
            'active_alerts': alerts.filter(is_resolved=False).count(),
            'resolved_alerts': alerts.filter(is_resolved=True).count(),
            'alerts_by_type': alerts.values('alert_type').annotate(
                count=models.Count('alert_type')
            ),
            'alerts_by_priority': alerts.values('priority').annotate(
                count=models.Count('priority')
            ),
            'average_resolution_time': self.calculate_average_resolution_time(alerts)
        }
    
    def calculate_average_resolution_time(self, alerts):
        """Calculate average resolution time"""
        resolved_alerts = alerts.filter(
            is_resolved=True,
            resolved_at__isnull=False
        )
        
        if not resolved_alerts.exists():
            return None
        
        total_time = 0
        for alert in resolved_alerts:
            delta = alert.resolved_at - alert.created_at
            total_time += delta.total_seconds()
        
        return total_time / resolved_alerts.count() / 3600  # hours
