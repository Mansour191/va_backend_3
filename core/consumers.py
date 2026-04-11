"""
WebSocket consumers for real-time notifications
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        # Only allow authenticated users
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Create user-specific group name
        self.user_group_name = f'notifications_{self.user.id}'
        
        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Join general notifications group (for broadcasts)
        await self.channel_layer.group_add(
            'notifications_broadcast',
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial unread count
        await self.send_unread_count()
        
        # Send recent notifications
        await self.send_recent_notifications()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        
        # Leave broadcast group
        await self.channel_layer.group_discard(
            'notifications_broadcast',
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)
                
            elif message_type == 'mark_all_read':
                await self.mark_all_notifications_read()
                
            elif message_type == 'delete':
                notification_id = data.get('notification_id')
                await self.delete_notification(notification_id)
                
            elif message_type == 'get_unread_count':
                await self.send_unread_count()
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(str(e))
    
    async def notification_message(self, event):
        """Handle incoming notification messages"""
        notification = event['notification']
        
        # Only send if notification is for this user or is broadcast
        if (notification.get('user_id') == self.user.id or 
            notification.get('recipient_type') == 'all' or
            (notification.get('recipient_type') == 'group' and 
             await self.user_in_group(notification.get('recipient_group')))):
            
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification
            }))
    
    async def unread_count_update(self, event):
        """Handle unread count updates"""
        if event.get('user_id') == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': event.get('count', 0)
            }))
    
    async def send_unread_count(self):
        """Send current unread count to user"""
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': count
        }))
    
    async def send_recent_notifications(self):
        """Send recent notifications to user"""
        notifications = await self.get_recent_notifications()
        await self.send(text_data=json.dumps({
            'type': 'recent_notifications',
            'notifications': notifications
        }))
    
    async def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        try:
            success = await self.update_notification_read_status(notification_id, True)
            if success:
                # Send updated unread count
                await self.send_unread_count()
                
                # Send confirmation
                await self.send(text_data=json.dumps({
                    'type': 'notification_marked_read',
                    'notification_id': notification_id
                }))
        except Exception as e:
            await self.send_error(str(e))
    
    async def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        try:
            count = await self.update_all_notifications_read()
            
            # Send updated unread count
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': 0
            }))
            
            # Send confirmation
            await self.send(text_data=json.dumps({
                'type': 'all_notifications_marked_read',
                'count': count
            }))
        except Exception as e:
            await self.send_error(str(e))
    
    async def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            success = await self.remove_notification(notification_id)
            if success:
                # Send updated unread count
                await self.send_unread_count()
                
                # Send confirmation
                await self.send(text_data=json.dumps({
                    'type': 'notification_deleted',
                    'notification_id': notification_id
                }))
        except Exception as e:
            await self.send_error(str(e))
    
    async def send_error(self, message):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notifications count for user"""
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def get_recent_notifications(self):
        """Get recent notifications for user"""
        notifications = Notification.objects.filter(
            user=self.user
        ).order_by('-created_at')[:10]
        
        return [
            {
                'id': n.id,
                'type': n.type,
                'title': n.title,
                'message': n.message,
                'priority': n.priority,
                'category': n.category,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'action_url': n.action_url,
                'action_text': n.action_text,
                'metadata': n.metadata
            }
            for n in notifications
        ]
    
    @database_sync_to_async
    def update_notification_read_status(self, notification_id, is_read):
        """Update notification read status"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = is_read
            if is_read:
                notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def update_all_notifications_read(self):
        """Mark all notifications as read for user"""
        count = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return count
    
    @database_sync_to_async
    def remove_notification(self, notification_id):
        """Delete a notification"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.delete()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def user_in_group(self, group_name):
        """Check if user is in a specific group"""
        if not group_name:
            return False
        
        return self.user.groups.filter(name=group_name).exists()


class AdminNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for admin notifications"""
    
    async def connect(self):
        """Handle WebSocket connection for admin users"""
        self.user = self.scope["user"]
        
        # Only allow admin users
        if not self.user.is_staff or self.user.is_anonymous:
            await self.close()
            return
        
        # Join admin notifications group
        await self.channel_layer.group_add(
            'admin_notifications',
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            'admin_notifications',
            self.channel_name
        )
    
    async def admin_notification(self, event):
        """Handle admin notification messages"""
        await self.send(text_data=json.dumps({
            'type': 'admin_notification',
            'notification': event['notification']
        }))
    
    async def system_alert(self, event):
        """Handle system alert messages"""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'alert': event['alert']
        }))
