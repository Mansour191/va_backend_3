"""
Notification Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    
    # Additional fields for API responses
    time_ago = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'type', 'sender', 
            'recipient_type', 'recipient_group', 'priority', 'category',
            'metadata', 'action_url', 'action_text', 'is_read', 
            'is_archived', 'read_at', 'expires_at', 'created_at', 
            'updated_at', 'time_ago', 'priority_display', 
            'category_display', 'type_display'
        ]
        read_only_fields = [
            'id', 'user', 'sender', 'read_at', 'created_at', 'updated_at',
            'time_ago', 'priority_display', 'category_display', 'type_display'
        ]

    def get_time_ago(self, obj):
        """Get human-readable time ago string"""
        import math
        
        if not obj.created_at:
            return ''
        
        now = timezone.now()
        diff = now - obj.created_at
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'الآن'
        elif seconds < 3600:
            minutes = math.floor(seconds / 60)
            return f'منذ {minutes} دقيقة'
        elif seconds < 86400:
            hours = math.floor(seconds / 3600)
            return f'منذ {hours} ساعة'
        elif seconds < 604800:
            days = math.floor(seconds / 86400)
            return f'منذ {days} يوم'
        else:
            return obj.created_at.strftime('%Y-%m-%d')

    def get_priority_display(self, obj):
        """Get priority display label"""
        labels = {
            'low': 'منخفض',
            'medium': 'متوسط',
            'high': 'عالي',
            'critical': 'حرج'
        }
        return labels.get(obj.priority, obj.priority)

    def get_category_display(self, obj):
        """Get category display label"""
        labels = {
            'finance': 'المالية',
            'inventory': 'المخزون',
            'order': 'الطلبات',
            'security': 'الأمان',
            'marketing': 'التسويق',
            'system': 'النظام',
            'logistics': 'اللوجستيات',
            'customer_service': 'خدمة العملاء'
        }
        return labels.get(obj.category, obj.category)

    def get_type_display(self, obj):
        """Get type display label"""
        labels = {
            'payment_success': 'نجاح الدفع',
            'payment_failed': 'فشل الدفع',
            'refund_processed': 'معالجة الاسترداد',
            'ccp_received': 'استلام تحويل CCP',
            'coupon_applied': 'تطبيق كوبون',
            'coupon_expired': 'انتهاء كوبون',
            'order_created': 'إنشاء طلب',
            'order_confirmed': 'تأكيد طلب',
            'order_cancelled': 'إلغاء طلب',
            'order_shipped': 'شحن طلب',
            'order_delivered': 'تسليم طلب',
            'order_returned': 'إرجاع طلب',
            'order_modified': 'تعديل طلب',
            'stock_low': 'مخزون منخفض',
            'stock_out': 'نفاد المخزون',
            'product_added': 'إضافة منتج',
            'product_updated': 'تحديث منتج',
            'login_new_device': 'تسجيل دخول من جهاز جديد',
            'password_changed': 'تغيير كلمة المرور',
            'login_failed': 'فشل تسجيل الدخول',
            'account_locked': 'قفل الحساب',
            'shipping_confirmed': 'تأكيد الشحن',
            'shipping_delayed': 'تأخير الشحن',
            'delivery_failed': 'فشل التسليم',
            'package_received': 'استلام الطرد',
            'system_maintenance': 'صيانة النظام',
            'system_update': 'تحديث النظام',
            'database_backup': 'نسخ احتياطي',
            'promotion_launched': 'إطلاق ترويج',
            'newsletter_sent': 'إرسال نشرة بريدية',
            'campaign_completed': 'اكتمال الحملة',
            'support_ticket_created': 'إنشاء تذكرة دعم',
            'support_ticket_resolved': 'حل تذكرة الدعم',
            'feedback_received': 'استلام ملاحظات',
            'cart_abandonment': 'إهمال السلة',
            'invoice_generated': 'إنشاء فاتورة',
            'payment_reminder': 'تذكير بالدفع',
            'coupon_expiry_reminder': 'تذكير انتهاء كوبون'
        }
        return labels.get(obj.type, obj.type)

    def validate_priority(self, value):
        """Validate priority field"""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if value not in valid_priorities:
            raise serializers.ValidationError(f'Priority must be one of: {valid_priorities}')
        return value

    def validate_category(self, value):
        """Validate category field"""
        valid_categories = [
            'finance', 'inventory', 'order', 'security', 
            'marketing', 'system', 'logistics', 'customer_service'
        ]
        if value not in valid_categories:
            raise serializers.ValidationError(f'Category must be one of: {valid_categories}')
        return value

    def validate_recipient_type(self, value):
        """Validate recipient type field"""
        valid_types = ['user', 'group', 'all', 'role']
        if value not in valid_types:
            raise serializers.ValidationError(f'Recipient type must be one of: {valid_types}')
        return value


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of user IDs for targeted notifications"
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'type', 'sender', 'recipient_type', 
            'recipient_group', 'priority', 'category', 'metadata', 
            'action_url', 'action_text', 'expires_at', 'user_ids'
        ]

    def create(self, validated_data):
        """Create notification with enhanced logic"""
        user_ids = validated_data.pop('user_ids', None)
        recipient_type = validated_data.get('recipient_type', 'user')
        
        if recipient_type == 'all':
            # Create broadcast notification
            notification = Notification.objects.create(**validated_data)
            
            # Create individual notifications for all active users
            users = User.objects.filter(is_active=True)
            
            created_notifications = []
            for user in users:
                user_notification = Notification.objects.create(
                    user=user,
                    **validated_data
                )
                created_notifications.append(user_notification)
            
            return created_notifications[0]  # Return first created notification
            
        elif recipient_type == 'users' and user_ids:
            # Create notifications for specific users
            users = User.objects.filter(id__in=user_ids, is_active=True)
            
            created_notifications = []
            for user in users:
                user_notification = Notification.objects.create(
                    user=user,
                    **validated_data
                )
                created_notifications.append(user_notification)
            
            return created_notifications[0] if created_notifications else None
            
        else:
            # Create single notification
            return super().create(validated_data)


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating notifications
    """
    
    class Meta:
        model = Notification
        fields = ['is_read', 'is_archived', 'read_at']
    
    def update(self, instance, validated_data):
        """Update notification with automatic read_at timestamp"""
        if validated_data.get('is_read') and not instance.is_read:
            validated_data['read_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer for notification statistics
    """
    
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    read = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    recent = serializers.IntegerField()
    by_category = serializers.ListField(
        child=serializers.DictField()
    )
    by_priority = serializers.ListField(
        child=serializers.DictField()
    )
    by_type = serializers.ListField(
        child=serializers.DictField()
    )


class BroadcastNotificationSerializer(serializers.Serializer):
    """
    Serializer for broadcast notifications
    """
    
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    recipient_type = serializers.ChoiceField(
        choices=['all', 'group', 'role', 'users']
    )
    recipient_group = serializers.CharField(
        required=False,
        allow_blank=True
    )
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'critical'],
        default='medium'
    )
    category = serializers.ChoiceField(
        choices=[
            'finance', 'inventory', 'order', 'security',
            'marketing', 'system', 'logistics', 'customer_service'
        ],
        default='system'
    )
    type = serializers.CharField(
        default='system_update'
    )
    action_url = serializers.URLField(
        required=False,
        allow_blank=True
    )
    action_text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100
    )
    metadata = serializers.JSONField(
        default=dict,
        required=False
    )
    schedule_at = serializers.DateTimeField(
        required=False,
        allow_null=True
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    def validate(self, attrs):
        """Validate broadcast notification data"""
        recipient_type = attrs.get('recipient_type')
        recipient_group = attrs.get('recipient_group')
        user_ids = attrs.get('user_ids')
        
        if recipient_type == 'group' and not recipient_group:
            raise serializers.ValidationError(
                'recipient_group is required when recipient_type is "group"'
            )
        
        if recipient_type == 'users' and not user_ids:
            raise serializers.ValidationError(
                'user_ids is required when recipient_type is "users"'
            )
        
        if attrs.get('action_text') and not attrs.get('action_url'):
            raise serializers.ValidationError(
                'action_url is required when action_text is provided'
            )
        
        return attrs


class NotificationPreferenceSerializer(serializers.Serializer):
    """
    Serializer for notification preferences
    """
    
    email_notifications = serializers.BooleanField(default=True)
    push_notifications = serializers.BooleanField(default=True)
    sms_notifications = serializers.BooleanField(default=False)
    categories = serializers.DictField(
        default=dict,
        child=serializers.BooleanField(),
        help_text="Category-wise notification preferences"
    )
    
    def validate_categories(self, value):
        """Validate category preferences"""
        valid_categories = [
            'order', 'finance', 'marketing', 'system', 
            'security', 'logistics', 'inventory', 'customer_service'
        ]
        
        for category in value:
            if category not in valid_categories:
                raise serializers.ValidationError(
                    f'Invalid category: {category}. Valid categories are: {valid_categories}'
                )
        
        return value
