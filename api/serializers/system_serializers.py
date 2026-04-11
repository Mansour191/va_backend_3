"""
System Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.system import Notification, ERPNextSyncLog, SystemConfiguration


class ERPNextSyncLogSerializer(serializers.ModelSerializer):
    """ERPNext sync log serializer"""
    can_retry = serializers.SerializerMethodField()
    
    class Meta:
        model = ERPNextSyncLog
        fields = [
            'id', 'sync_id', 'action', 'entity_type',
            'status', 'progress_percentage', 'records_total',
            'records_synced', 'records_failed', 'records_skipped',
            'started_at', 'completed_at', 'duration_seconds',
            'error_message', 'error_details', 'retry_count',
            'max_retries', 'sync_data', 'response_data',
            'api_calls_count', 'data_size_bytes',
            'average_response_time', 'triggered_by',
            'system_version', 'api_version', 'can_retry'
        ]
        read_only_fields = ['id', 'started_at']
    
    def get_can_retry(self, obj):
        """Check if sync can be retried"""
        return obj.can_retry


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """System configuration serializer"""
    organization_name = serializers.CharField(
        source='organization.name', read_only=True, allow_null=True
    )
    
    class Meta:
        model = SystemConfiguration
        fields = [
            'id', 'key', 'value', 'config_type', 'data_type',
            'is_required', 'default_value', 'min_value',
            'max_value', 'allowed_values', 'validation_regex',
            'is_public', 'is_editable', 'requires_restart',
            'organization', 'organization_name', 'environment',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_typed_value(self):
        """Get value in correct data type"""
        return self.get_typed_value()


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'title', 'message', 'type',
            'sender', 'recipient_type', 'recipient_group',
            'recipient_segment', 'priority', 'category',
            'metadata', 'action_url', 'action_text',
            'action_button_color', 'is_read', 'is_archived',
            'is_starred', 'read_at', 'expires_at',
            'data', 'delivery_channels', 'delivery_status',
            'created_at', 'updated_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        """Check if notification is expired"""
        return obj.is_expired


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Notification creation serializer"""
    class Meta:
        model = Notification
        fields = [
            'user', 'title', 'message', 'type', 'sender',
            'recipient_type', 'recipient_group', 'recipient_segment',
            'priority', 'category', 'metadata', 'action_url',
            'action_text', 'action_button_color', 'expires_at',
            'data'
        ]
    
    def validate(self, data):
        """Validate notification data"""
        recipient_type = data.get('recipient_type')
        
        if recipient_type == 'user' and not data.get('user'):
            raise serializers.ValidationError(
                "User is required when recipient_type is 'user'"
            )
        
        return data
    
    def create(self, validated_data):
        """Create notification"""
        return Notification.objects.create(**validated_data)


class SystemConfigurationCreateSerializer(serializers.ModelSerializer):
    """System configuration creation serializer"""
    class Meta:
        model = SystemConfiguration
        fields = [
            'key', 'value', 'config_type', 'data_type',
            'is_required', 'default_value', 'min_value',
            'max_value', 'allowed_values', 'validation_regex',
            'is_public', 'is_editable', 'requires_restart',
            'organization', 'environment'
        ]
    
    def validate_key(self, value):
        """Validate key uniqueness"""
        filters = {'key': value}
        
        if self.instance:
            # For update, exclude current instance
            filters['id__ne'] = self.instance.id
        
        if SystemConfiguration.objects.filter(**filters).exists():
            raise serializers.ValidationError(
                "Configuration key already exists"
            )
        return value
    
    def validate(self, data):
        """Validate configuration data"""
        value = data.get('value')
        data_type = data.get('data_type')
        min_value = data.get('min_value')
        max_value = data.get('max_value')
        allowed_values = data.get('allowed_values', [])
        
        # Type validation
        if data_type == 'integer':
            try:
                int(value)
            except ValueError:
                raise serializers.ValidationError(
                    "Value must be an integer"
                )
        elif data_type == 'float':
            try:
                float(value)
            except ValueError:
                raise serializers.ValidationError(
                    "Value must be a number"
                )
        elif data_type == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0']:
                raise serializers.ValidationError(
                    "Value must be true or false"
                )
        elif data_type == 'json':
            import json
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    "Value must be valid JSON"
                )
        
        # Range validation
        if min_value is not None:
            try:
                if float(value) < min_value:
                    raise serializers.ValidationError(
                        f"Value must be at least {min_value}"
                    )
            except ValueError:
                pass
        
        if max_value is not None:
            try:
                if float(value) > max_value:
                    raise serializers.ValidationError(
                        f"Value must be at most {max_value}"
                    )
            except ValueError:
                pass
        
        # Allowed values validation
        if allowed_values and value not in allowed_values:
            raise serializers.ValidationError(
                f"Value must be one of: {', '.join(map(str, allowed_values))}"
            )
        
        return data
    
    def create(self, validated_data):
        """Create system configuration"""
        user = self.context['request'].user
        validated_data['created_by'] = user
        return SystemConfiguration.objects.create(**validated_data)


class SystemConfigurationUpdateSerializer(serializers.ModelSerializer):
    """System configuration update serializer"""
    class Meta:
        model = SystemConfiguration
        fields = [
            'value', 'data_type', 'is_required', 'default_value',
            'min_value', 'max_value', 'allowed_values',
            'validation_regex', 'is_public', 'is_editable',
            'requires_restart', 'organization', 'environment'
        ]
    
    def validate(self, data):
        """Validate configuration data"""
        value = data.get('value')
        data_type = data.get('data_type')
        min_value = data.get('min_value')
        max_value = data.get('max_value')
        allowed_values = data.get('allowed_values', [])
        
        # Type validation
        if data_type == 'integer':
            try:
                int(value)
            except ValueError:
                raise serializers.ValidationError(
                    "Value must be an integer"
                )
        elif data_type == 'float':
            try:
                float(value)
            except ValueError:
                raise serializers.ValidationError(
                    "Value must be a number"
                )
        elif data_type == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0']:
                raise serializers.ValidationError(
                    "Value must be true or false"
                )
        elif data_type == 'json':
            import json
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    "Value must be valid JSON"
                )
        
        # Range validation
        if min_value is not None:
            try:
                if float(value) < min_value:
                    raise serializers.ValidationError(
                        f"Value must be at least {min_value}"
                    )
            except ValueError:
                pass
        
        if max_value is not None:
            try:
                if float(value) > max_value:
                    raise serializers.ValidationError(
                        f"Value must be at most {max_value}"
                    )
            except ValueError:
                pass
        
        # Allowed values validation
        if allowed_values and value not in allowed_values:
            raise serializers.ValidationError(
                f"Value must be one of: {', '.join(map(str, allowed_values))}"
            )
        
        return data
    
    def update(self, instance, validated_data):
        """Update system configuration"""
        user = self.context['request'].user
        validated_data['updated_by'] = user
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class NotificationActionSerializer(serializers.Serializer):
    """Notification action serializer"""
    action = serializers.ChoiceField(
        choices=['mark_read', 'archive', 'star', 'unstar'],
        required=True
    )
    notification_id = serializers.IntegerField(required=True)
    
    def validate_notification_id(self, value):
        """Validate notification exists"""
        if not Notification.objects.filter(id=value).exists():
            raise serializers.ValidationError("Notification not found")
        return value
    
    def save(self):
        """Execute notification action"""
        action = self.validated_data['action']
        notification_id = self.validated_data['notification_id']
        user = self.context['request'].user
        
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # Check ownership
            if notification.user != user:
                return {'status': 'error', 'message': 'Access denied'}
            
            if action == 'mark_read':
                notification.mark_as_read()
                return {'status': 'success', 'message': 'Marked as read'}
            
            elif action == 'archive':
                notification.archive()
                return {'status': 'success', 'message': 'Archived'}
            
            elif action == 'star':
                notification.star()
                return {'status': 'success', 'message': 'Starred'}
            
            elif action == 'unstar':
                notification.unstar()
                return {'status': 'success', 'message': 'Unstarred'}
        
        except Notification.DoesNotExist:
            return {'status': 'error', 'message': 'Notification not found'}


class SyncTriggerSerializer(serializers.Serializer):
    """Sync trigger serializer"""
    entity_type = serializers.ChoiceField(
        choices=['products', 'orders', 'customers', 'inventory', 'all'],
        required=True
    )
    action = serializers.CharField(required=True)
    
    def save(self):
        """Trigger ERPNext sync"""
        entity_type = self.validated_data['entity_type']
        action = self.validated_data['action']
        user = self.context['request'].user
        
        sync_id = f"{entity_type}_{action}_{timezone.now().timestamp()}"
        
        sync_log = ERPNextSyncLog.objects.create(
            sync_id=sync_id,
            action=action,
            entity_type=entity_type,
            status='running',
            triggered_by=user
        )
        
        return {
            'status': 'success',
            'sync_id': sync_id,
            'message': f'Sync triggered for {entity_type}'
        }
