"""
Comprehensive Notification System Signals
This file contains signals that automatically create notifications for all business events:
- Sales and Orders
- Finance and Payments
- Inventory and Products
- Security and Accounts
- Logistics and Shipping
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import json

from core.models import Notification, Product, CartItem
from .models import Order, OrderTimeline, Payment, Coupon

User = get_user_model()


def create_order_timeline_entry(order, old_status=None):
    """Create OrderTimeline entry with appropriate message"""
    status_messages = {
        'pending': 'تم استلام الطلب وجاري المعالجة',
        'confirmed': 'تم تأكيد الطلب',
        'processing': 'جاري تجهيز الطلب',
        'shipped': 'تم شحن الطلب',
        'delivered': 'تم تسليم الطلب',
        'cancelled': 'تم إلغاء الطلب',
        'refunded': 'تم استرداد المبلغ',
        'returned': 'تم إرجاع الطلب'
    }
    
    default_note = status_messages.get(order.status, f'تغير حالة الطلب إلى: {order.status}')
    
    # Add transition context if old status exists
    if old_status and old_status != order.status:
        default_note = f'تغير الحالة من "{old_status}" إلى "{order.status}"'
    
    # Create timeline entry
    OrderTimeline.objects.create(
        order=order,
        status=order.status,
        note=default_note,
        user=None  # System generated
    )


class NotificationEngine:
    """Central notification engine for creating and managing notifications"""
    
    @staticmethod
    def create_notification(notification_type, title, message, user=None, 
                          recipient_type='user', priority='medium', category='system',
                          metadata=None, action_url=None, action_text=None,
                          sender='system', recipient_group=None):
        """Create a notification with all enhanced fields"""
        
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            sender=sender,
            recipient_type=recipient_type,
            recipient_group=recipient_group,
            priority=priority,
            category=category,
            metadata=metadata or {},
            action_url=action_url,
            action_text=action_text
        )
        
        # Handle broadcast notifications
        if recipient_type == 'all':
            NotificationEngine.broadcast_notification(notification)
        elif recipient_type == 'group' and recipient_group:
            NotificationEngine.group_notification(notification, recipient_group)
        elif recipient_type == 'role' and recipient_group:
            NotificationEngine.role_notification(notification, recipient_group)
            
        return notification
    
    @staticmethod
    def broadcast_notification(notification):
        """Send notification to all users"""
        users = User.objects.filter(is_active=True)
        for user in users:
            Notification.objects.create(
                user=user,
                type=notification.type,
                title=notification.title,
                message=notification.message,
                sender=notification.sender,
                recipient_type='user',
                priority=notification.priority,
                category=notification.category,
                metadata=notification.metadata,
                action_url=notification.action_url,
                action_text=notification.action_text
            )
    
    @staticmethod
    def group_notification(notification, group_name):
        """Send notification to specific user group"""
        try:
            from django.contrib.auth.models import Group
            group = Group.objects.get(name=group_name)
            users = group.user_set.filter(is_active=True)
            for user in users:
                Notification.objects.create(
                    user=user,
                    type=notification.type,
                    title=notification.title,
                    message=notification.message,
                    sender=notification.sender,
                    recipient_type='user',
                    priority=notification.priority,
                    category=notification.category,
                    metadata=notification.metadata,
                    action_url=notification.action_url,
                    action_text=notification.action_text
                )
        except Group.DoesNotExist:
            pass
    
    @staticmethod
    def role_notification(notification, role_name):
        """Send notification to users with specific role"""
        # This depends on your role system implementation
        pass


# ================================
# SALES AND ORDERS SIGNALS
# ================================

@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    """Create notification when new order is created"""
    if created:
        # Create initial timeline entry for new order
        create_order_timeline_entry(instance)
        
        NotificationEngine.create_notification(
            notification_type='order_created',
            title='🛒 طلب جديد',
            message=f'تم استلام طلب جديد رقم {instance.order_number} بقيمة {instance.total_amount} د.ج',
            user=instance.user,
            priority='high',
            category='order',
            metadata={
                'order_id': instance.id,
                'order_number': instance.order_number,
                'total_amount': float(instance.total_amount),
                'customer_name': instance.customer_name
            },
            action_url=f'/admin/orders/{instance.id}/',
            action_text='عرض الطلب'
        )


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """Track order status changes before saving"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def order_status_changed_notification(sender, instance, created, **kwargs):
    """Create notification when order status changes"""
    if not created:
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            
            # Create OrderTimeline entry
            create_order_timeline_entry(instance, old_status)
            
            status_messages = {
                'confirmed': ('✅ تأكيد الطلب', f'تم تأكيد طلبك رقم {instance.order_number} وجاري تحضيره'),
                'processing': ('⚙️ المعالجة', f'طلبك رقم {instance.order_number} قيد المعالجة'),
                'shipped': ('🚚 الشحن', f'تم شحن طلبك رقم {instance.order_number}'),
                'delivered': ('🏠 التسليم', f'تم تسليم طلبك رقم {instance.order_number} بنجاح'),
                'cancelled': ('❌ إلغاء الطلب', f'تم إلغاء طلبك رقم {instance.order_number}')
            }
            
            if instance.status in status_messages:
                title, message = status_messages[instance.status]
                NotificationEngine.create_notification(
                    notification_type=f'order_{instance.status}',
                    title=title,
                    message=message,
                    user=instance.user,
                    priority='medium',
                    category='order',
                    metadata={
                        'order_id': instance.id,
                        'order_number': instance.order_number,
                        'old_status': old_status,
                        'new_status': instance.status
                    },
                    action_url=f'/orders/{instance.order_number}/',
                    action_text='عرض التفاصيل'
                )


@receiver(post_save, sender=Order)
def order_cancelled_notification(sender, instance, created, **kwargs):
    """Special notification for order cancellation"""
    if not created and instance.status == 'cancelled':
        old_status = getattr(instance, '_old_status', None)
        if old_status != 'cancelled':
            NotificationEngine.create_notification(
                notification_type='order_cancelled',
                title='❌ إلغاء الطلب',
                message=f'تم إلغاء طلبك رقم {instance.order_number}. سنتواصل معك قريباً',
                user=instance.user,
                priority='high',
                category='order',
                metadata={
                    'order_id': instance.id,
                    'order_number': instance.order_number,
                    'cancellation_reason': getattr(instance, 'cancellation_reason', '')
                }
            )


# ================================
# FINANCE AND PAYMENTS SIGNALS
# ================================

@receiver(post_save, sender=Payment)
def payment_notification(sender, instance, created, **kwargs):
    """Create notifications for payment events"""
    if created:
        if instance.status == 'completed':
            NotificationEngine.create_notification(
                notification_type='payment_success',
                title='💳 تأكيد الدفع',
                message=f'تم تأكيد دفع مبلغ {instance.amount} د.ج للطلب رقم {instance.order.order_number}',
                user=instance.order.user,
                priority='high',
                category='finance',
                metadata={
                    'payment_id': instance.id,
                    'order_id': instance.order.id,
                    'order_number': instance.order.order_number,
                    'amount': float(instance.amount),
                    'method': instance.method
                },
                action_url=f'/orders/{instance.order.order_number}/invoice/',
                action_text='عرض الفاتورة'
            )
            
        elif instance.status == 'failed':
            NotificationEngine.create_notification(
                notification_type='payment_failed',
                title='❌ فشل الدفع',
                message=f'فشل عملية الدفع للطلب رقم {instance.order.order_number}. يرجى المحاولة مرة أخرى',
                user=instance.order.user,
                priority='high',
                category='finance',
                metadata={
                    'payment_id': instance.id,
                    'order_id': instance.order.id,
                    'order_number': instance.order.order_number,
                    'amount': float(instance.amount),
                    'method': instance.method
                },
                action_url=f'/orders/{instance.order.order_number}/payment/',
                action_text='إعادة الدفع'
            )


@receiver(post_save, sender=Coupon)
def coupon_notification(sender, instance, created, **kwargs):
    """Create notifications for coupon events"""
    if created:
        # Notify all users about new coupon
        NotificationEngine.create_notification(
            notification_type='coupon_applied',
            title='🎁 كوبون خصم جديد!',
            message=f'كوبون جديد: {instance.code} - خصم {instance.discount_value}{"%" if instance.discount_type == "percentage" else " د.ج"}',
            recipient_type='all',
            priority='medium',
            category='marketing',
            metadata={
                'coupon_id': instance.id,
                'code': instance.code,
                'discount_type': instance.discount_type,
                'discount_value': float(instance.discount_value)
            },
            action_url='/coupons/',
            action_text='استخدم الكوبون'
        )


# ================================
# INVENTORY AND PRODUCTS SIGNALS
# ================================

@receiver(post_save, sender=Product)
def product_notification(sender, instance, created, **kwargs):
    """Create notifications for product events"""
    if created:
        # Notify admins about new product
        NotificationEngine.create_notification(
            notification_type='product_added',
            title='📦 منتج جديد',
            message=f'تم إضافة منتج جديد: {instance.name_ar}',
            recipient_type='group',
            recipient_group='inventory_managers',
            priority='medium',
            category='inventory',
            metadata={
                'product_id': instance.id,
                'product_name': instance.name_ar,
                'price': float(instance.base_price)
            },
            action_url=f'/admin/products/{instance.id}/',
            action_text='عرض المنتج'
        )


@receiver(post_save, sender=Product)
def stock_alert_notification(sender, instance, created, **kwargs):
    """Create notification when stock is low"""
    if not created and instance.stock <= 5:  # Alert when stock is 5 or less
        NotificationEngine.create_notification(
            notification_type='stock_low',
            title='⚠️ مخزون منخفض',
            message=f'المخزون منخفض للمنتج: {instance.name_ar} - الكمية المتبقية: {instance.stock}',
            recipient_type='group',
            recipient_group='inventory_managers',
            priority='high',
            category='inventory',
            metadata={
                'product_id': instance.id,
                'product_name': instance.name_ar,
                'current_stock': instance.stock,
                'reorder_point': 5
            },
            action_url=f'/admin/products/{instance.id}/',
            action_text='تحديث المخزون'
        )


# ================================
# SECURITY AND ACCOUNTS SIGNALS
# ================================

@receiver(post_save, sender=User)
def user_security_notification(sender, instance, created, **kwargs):
    """Create notifications for user security events"""
    if not created:
        # Check if password was recently changed
        if hasattr(instance, '_password_changed') and instance._password_changed:
            NotificationEngine.create_notification(
                notification_type='password_changed',
                title='🔒 تغيير كلمة المرور',
                message='تم تغيير كلمة المرور الخاصة بحسابك بنجاح',
                user=instance,
                priority='high',
                category='security',
                metadata={
                    'user_id': instance.id,
                    'timestamp': timezone.now().isoformat()
                }
            )


# Custom signal for login tracking
def user_login_notification(sender, request, user, **kwargs):
    """Create notification for login from new device"""
    # This would be called from your login view
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_address = request.META.get('REMOTE_ADDR', '')
    
    NotificationEngine.create_notification(
        notification_type='login_new_device',
        title='🔐 تسجيل دخول جديد',
        message=f'تم تسجيل الدخول إلى حسابك من جهاز جديد. IP: {ip_address}',
        user=user,
        priority='medium',
        category='security',
        metadata={
            'user_agent': user_agent,
            'ip_address': ip_address,
            'timestamp': timezone.now().isoformat()
        }
    )


# ================================
# LOGISTICS AND SHIPPING SIGNALS
# ================================

@receiver(post_save, sender=Order)
def shipping_notification(sender, instance, created, **kwargs):
    """Create notifications for shipping events"""
    if not created and instance.status == 'shipped':
        if hasattr(instance, 'tracking_number') and instance.tracking_number:
            NotificationEngine.create_notification(
                notification_type='shipping_confirmed',
                title='🚚 تأكيد الشحن',
                message=f'تم شحن طلبك رقم {instance.order_number} - رقم التتبع: {instance.tracking_number}',
                user=instance.user,
                priority='medium',
                category='logistics',
                metadata={
                    'order_id': instance.id,
                    'order_number': instance.order_number,
                    'tracking_number': instance.tracking_number
                },
                action_url=f'/track/{instance.tracking_number}/',
                action_text='تتبع الشحنة'
            )


# ================================
# SMART AUTOMATION SIGNALS
# ================================

@receiver(post_save, sender=CartItem)
def cart_abandonment_reminder(sender, instance, created, **kwargs):
    """Schedule reminder for abandoned cart (this would be handled by a scheduled task)"""
    pass  # This would be implemented in a management command


# ================================
# ADMIN BROADCAST SYSTEM
# ================================

class AdminBroadcast:
    """System for admin to send broadcast notifications"""
    
    @staticmethod
    def send_broadcast(title, message, priority='medium', category='marketing', 
                       action_url=None, action_text=None, sender='admin'):
        """Send broadcast to all users"""
        return NotificationEngine.create_notification(
            notification_type='system_update',
            title=title,
            message=message,
            recipient_type='all',
            priority=priority,
            category=category,
            action_url=action_url,
            action_text=action_text,
            sender=sender
        )
    
    @staticmethod
    def send_to_group(title, message, group_name, priority='medium', 
                     category='system', action_url=None, action_text=None):
        """Send notification to specific user group"""
        return NotificationEngine.create_notification(
            notification_type='system_update',
            title=title,
            message=message,
            recipient_type='group',
            recipient_group=group_name,
            priority=priority,
            category=category,
            action_url=action_url,
            action_text=action_text,
            sender='admin'
        )


# ================================
# NOTIFICATION CLEANUP
# ================================

def cleanup_old_notifications():
    """Clean up old notifications (should be called by scheduled task)"""
    from datetime import timedelta
    
    # Delete general notifications older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    Notification.objects.filter(
        created_at__lt=cutoff_date,
        category__in=['marketing', 'system'],
        is_read=True
    ).delete()
    
    # Archive important financial notifications
    Notification.objects.filter(
        created_at__lt=cutoff_date,
        category='finance',
        is_read=True
    ).update(is_archived=True)
