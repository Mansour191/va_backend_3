"""
Smart Notification Automation Management Command
This command handles:
1. Cart abandonment reminders
2. Invoice notifications
3. Notification cleanup
4. Stock alerts
5. Scheduled notifications
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from datetime import timedelta, datetime
import logging

from core.models import Notification, Product, CartItem
from api.models import Order, Payment, Coupon

User = get_user_model()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run smart notification automation tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['cart-reminders', 'invoice-notifications', 'cleanup', 'stock-alerts', 'scheduled', 'all'],
            default='all',
            help='Specific task to run (default: all)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually sending notifications'
        )

    def handle(self, *args, **options):
        task = options['task']
        dry_run = options['dry_run']
        
        self.stdout.write(f"🤖 Starting notification automation - Task: {task}")
        
        if dry_run:
            self.stdout.write("🔍 DRY RUN MODE - No notifications will be sent")
        
        try:
            if task in ['cart-reminders', 'all']:
                self.send_cart_abandonment_reminders(dry_run)
            
            if task in ['invoice-notifications', 'all']:
                self.send_invoice_notifications(dry_run)
            
            if task in ['cleanup', 'all']:
                self.cleanup_old_notifications(dry_run)
            
            if task in ['stock-alerts', 'all']:
                self.send_stock_alerts(dry_run)
            
            if task in ['scheduled', 'all']:
                self.send_scheduled_notifications(dry_run)
                
            self.stdout.write(self.style.SUCCESS("✅ Automation completed successfully"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Automation failed: {str(e)}"))
            logger.error(f"Notification automation failed: {str(e)}")

    def send_cart_abandonment_reminders(self, dry_run=False):
        """Send reminders for abandoned carts (older than 24 hours)"""
        self.stdout.write("🛒 Processing cart abandonment reminders...")
        
        # Get carts abandoned more than 24 hours ago but less than 7 days
        cutoff_time = timezone.now() - timedelta(hours=24)
        week_ago = timezone.now() - timedelta(days=7)
        
        abandoned_carts = CartItem.objects.filter(
            updated_at__lt=cutoff_time,
            updated_at__gt=week_ago
        ).select_related('user', 'product').distinct('user')
        
        count = 0
        for cart_item in abandoned_carts:
            if not cart_item.user:
                continue
                
            # Check if we already sent a reminder recently
            recent_reminder = Notification.objects.filter(
                user=cart_item.user,
                type='cart_abandonment',
                created_at__gt=cutoff_time
            ).exists()
            
            if recent_reminder:
                continue
            
            # Get cart details
            cart_items = CartItem.objects.filter(user=cart_item.user)
            total_value = sum(item.quantity * item.product.base_price for item in cart_items)
            
            if dry_run:
                self.stdout.write(f"  📧 Would send reminder to {cart_item.user.username} - Cart value: {total_value}")
                count += 1
                continue
            
            # Create notification
            Notification.objects.create(
                user=cart_item.user,
                type='cart_abandonment',
                title='🛒 سلة التسوق في انتظارك!',
                message=f'لديك منتجات في سلة التسوق بقيمة {total_value:.2f} د.ج. أكمل عملية الشراء الآن!',
                priority='medium',
                category='marketing',
                metadata={
                    'cart_value': float(total_value),
                    'item_count': cart_items.count(),
                    'abandoned_hours': 24
                },
                action_url='/cart/',
                action_text='عرض السلة'
            )
            
            count += 1
        
        self.stdout.write(f"  📊 Processed {count} cart abandonment reminders")

    def send_invoice_notifications(self, dry_run=False):
        """Send invoice notifications for completed payments"""
        self.stdout.write("🧾 Processing invoice notifications...")
        
        # Get payments completed in the last hour that don't have invoice notifications
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        recent_payments = Payment.objects.filter(
            status='completed',
            created_at__gt=one_hour_ago
        ).select_related('order', 'order__user')
        
        count = 0
        for payment in recent_payments:
            # Check if invoice notification already sent
            existing_notification = Notification.objects.filter(
                user=payment.order.user,
                type='invoice_generated',
                metadata__payment_id=payment.id
            ).exists()
            
            if existing_notification:
                continue
            
            if dry_run:
                self.stdout.write(f"  📄 Would send invoice to {payment.order.user.username} - Payment: {payment.id}")
                count += 1
                continue
            
            # Create invoice notification
            Notification.objects.create(
                user=payment.order.user,
                type='invoice_generated',
                title='🧾 فاتورة جديدة',
                message=f'تم إنشاء فاتورة للطلب رقم {payment.order.order_number} بمبلغ {payment.amount} د.ج',
                priority='high',
                category='finance',
                metadata={
                    'payment_id': payment.id,
                    'order_id': payment.order.id,
                    'order_number': payment.order.order_number,
                    'amount': float(payment.amount),
                    'method': payment.method
                },
                action_url=f'/orders/{payment.order.order_number}/invoice/',
                action_text='عرض الفاتورة'
            )
            
            count += 1
        
        self.stdout.write(f"  📊 Processed {count} invoice notifications")

    def cleanup_old_notifications(self, dry_run=False):
        """Clean up old notifications based on rules"""
        self.stdout.write("🧹 Cleaning up old notifications...")
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        ninety_days_ago = timezone.now() - timedelta(days=90)
        
        # Delete read general notifications older than 30 days
        general_to_delete = Notification.objects.filter(
            created_at__lt=thirty_days_ago,
            is_read=True,
            category__in=['marketing', 'system']
        )
        
        # Archive important financial notifications older than 90 days
        financial_to_archive = Notification.objects.filter(
            created_at__lt=ninety_days_ago,
            category='finance',
            is_read=True,
            is_archived=False
        )
        
        # Delete low priority system notifications older than 7 days
        system_to_delete = Notification.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=7),
            category='system',
            priority='low',
            is_read=True
        )
        
        if dry_run:
            self.stdout.write(f"  🗑️  Would delete {general_to_delete.count()} general notifications")
            self.stdout.write(f"  📁 Would archive {financial_to_archive.count()} financial notifications")
            self.stdout.write(f"  🗑️  Would delete {system_to_delete.count()} system notifications")
            return
        
        # Perform cleanup
        general_deleted = general_to_delete.delete()[0]
        financial_archived = financial_to_archive.update(is_archived=True)
        system_deleted = system_to_delete.delete()[0]
        
        self.stdout.write(f"  🗑️  Deleted {general_deleted} general notifications")
        self.stdout.write(f"  📁 Archived {financial_archived} financial notifications")
        self.stdout.write(f"  🗑️  Deleted {system_deleted} system notifications")

    def send_stock_alerts(self, dry_run=False):
        """Send stock alerts for low inventory"""
        self.stdout.write("📦 Processing stock alerts...")
        
        # Get products with low stock
        low_stock_products = Product.objects.filter(
            stock__lte=5,
            is_active=True
        )
        
        count = 0
        for product in low_stock_products:
            # Check if we already sent an alert today
            today = timezone.now().date()
            existing_alert = Notification.objects.filter(
                type='stock_low',
                metadata__product_id=product.id,
                created_at__date=today
            ).exists()
            
            if existing_alert:
                continue
            
            # Send to inventory managers
            if dry_run:
                self.stdout.write(f"  📦 Would send stock alert for {product.name_ar} - Stock: {product.stock}")
                count += 1
                continue
            
            # Create notification for inventory managers
            Notification.objects.create(
                user=None,  # Broadcast
                type='stock_low',
                title='⚠️ مخزون منخفض',
                message=f'المخزون منخفض للمنتج: {product.name_ar} - الكمية المتبقية: {product.stock}',
                priority='high',
                category='inventory',
                recipient_type='group',
                recipient_group='inventory_managers',
                metadata={
                    'product_id': product.id,
                    'product_name': product.name_ar,
                    'current_stock': product.stock,
                    'reorder_point': 5
                },
                action_url=f'/admin/products/{product.id}/',
                action_text='تحديث المخزون'
            )
            
            count += 1
        
        self.stdout.write(f"  📊 Processed {count} stock alerts")

    def send_scheduled_notifications(self, dry_run=False):
        """Send scheduled notifications"""
        self.stdout.write("⏰ Processing scheduled notifications...")
        
        now = timezone.now()
        
        # Get scheduled notifications that are ready to send
        scheduled = Notification.objects.filter(
            created_at__lte=now,
            metadata__schedule_at__lte=now.isoformat(),
            metadata__sent=False
        )
        
        count = 0
        for notification in scheduled:
            if dry_run:
                self.stdout.write(f"  📤 Would send scheduled notification to {notification.user.username if notification.user else 'broadcast'}")
                count += 1
                continue
            
            # Update metadata to mark as sent
            notification.metadata['sent'] = True
            notification.metadata['sent_at'] = now.isoformat()
            notification.save(update_fields=['metadata'])
            
            # If it's a broadcast, create individual notifications
            if notification.recipient_type == 'all':
                users = User.objects.filter(is_active=True)
                for user in users:
                    Notification.objects.create(
                        user=user,
                        type=notification.type,
                        title=notification.title,
                        message=notification.message,
                        priority=notification.priority,
                        category=notification.category,
                        metadata=notification.metadata,
                        action_url=notification.action_url,
                        action_text=notification.action_text
                    )
                
                # Delete the original broadcast notification
                notification.delete()
            else:
                # For targeted notifications, just update the original
                pass
            
            count += 1
        
        self.stdout.write(f"  📊 Processed {count} scheduled notifications")

    def send_payment_reminders(self, dry_run=False):
        """Send payment reminders for pending payments"""
        self.stdout.write("💳 Processing payment reminders...")
        
        # Get pending payments older than 1 hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        pending_payments = Payment.objects.filter(
            status='pending',
            created_at__lt=one_hour_ago
        ).select_related('order', 'order__user')
        
        count = 0
        for payment in pending_payments:
            # Check if we already sent a reminder
            recent_reminder = Notification.objects.filter(
                user=payment.order.user,
                type='payment_reminder',
                metadata__payment_id=payment.id,
                created_at__gt=one_hour_ago
            ).exists()
            
            if recent_reminder:
                continue
            
            if dry_run:
                self.stdout.write(f"  💳 Would send payment reminder to {payment.order.user.username} - Amount: {payment.amount}")
                count += 1
                continue
            
            # Create payment reminder
            Notification.objects.create(
                user=payment.order.user,
                type='payment_reminder',
                title='💳 تذكير بالدفع',
                message=f'لديك دفع معلق للطلب رقم {payment.order.order_number} بمبلغ {payment.amount} د.ج',
                priority='high',
                category='finance',
                metadata={
                    'payment_id': payment.id,
                    'order_id': payment.order.id,
                    'order_number': payment.order.order_number,
                    'amount': float(payment.amount),
                    'method': payment.method
                },
                action_url=f'/orders/{payment.order.order_number}/payment/',
                action_text='إتمام الدفع'
            )
            
            count += 1
        
        self.stdout.write(f"  📊 Processed {count} payment reminders")

    def send_coupon_expiry_reminders(self, dry_run=False):
        """Send reminders for expiring coupons"""
        self.stdout.write("🎫 Processing coupon expiry reminders...")
        
        # Get coupons expiring in the next 3 days
        three_days_from_now = timezone.now() + timedelta(days=3)
        
        expiring_coupons = Coupon.objects.filter(
            valid_to__lte=three_days_from_now,
            valid_to__gt=timezone.now(),
            is_active=True
        )
        
        count = 0
        for coupon in expiring_coupons:
            # Check if we already sent a reminder today
            today = timezone.now().date()
            existing_reminder = Notification.objects.filter(
                type='coupon_expiry_reminder',
                metadata__coupon_id=coupon.id,
                created_at__date=today
            ).exists()
            
            if existing_reminder:
                continue
            
            if dry_run:
                self.stdout.write(f"  🎫 Would send expiry reminder for coupon {coupon.code}")
                count += 1
                continue
            
            # Create broadcast notification about expiring coupon
            Notification.objects.create(
                user=None,  # Broadcast
                type='coupon_expiry_reminder',
                title='🎫 كوبون على وشك الانتهاء',
                message=f'كوبون {coupon.code} سينتهي خلال 3 أيام. استخدمه الآن واحصل على خصم {coupon.discount_value}{"%" if coupon.discount_type == "percentage" else " د.ج"}!',
                priority='medium',
                category='marketing',
                recipient_type='all',
                metadata={
                    'coupon_id': coupon.id,
                    'code': coupon.code,
                    'discount_type': coupon.discount_type,
                    'discount_value': float(coupon.discount_value),
                    'expiry_date': coupon.valid_to.isoformat()
                },
                action_url='/coupons/',
                action_text='استخدم الكوبون'
            )
            
            count += 1
        
        self.stdout.write(f"  📊 Processed {count} coupon expiry reminders")
