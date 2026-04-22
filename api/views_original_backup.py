"""
API Views for Notification System - DISABLED
All REST API views have been commented out to enforce GraphQL-only architecture.
Only HealthView remains active for monitoring purposes.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone


# All REST API views have been disabled to enforce GraphQL-only architecture
# The following imports and classes are commented out:
#
# from rest_framework import viewsets, status, permissions
# from rest_framework.decorators import action
# from django.contrib.auth import get_user_model
# from django.db.models import Q, Count
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# import json
#
# from core.models import Notification, Shipping, CartItem, Product, Material, Coupon
# from core.serializers import (
#     NotificationSerializer, ShippingSerializer, CartItemSerializer, 
#     BroadcastNotificationSerializer
# )
# from .signals import NotificationEngine, AdminBroadcast
#
# User = get_user_model()


# Disabled REST API View Classes:
# - NotificationViewSet
# - CartView
# - ClearCartView
# - MergeCartView
# - WilayasView
# - WilayaDetailView
# - BulkUpdateShippingView
# - CalculateShippingView
# - apply_coupon_to_cart
# - set_shipping_for_cart
# - AdminBroadcastView
# - NotificationPreferencesView
# - NotificationSearchView
# - NotificationCountView

# All REST endpoints are disabled. Use GraphQL instead.
# GraphQL endpoint: /api/graphql/
# GraphQL batch endpoint: /api/graphql/batch/
#     """
#     ViewSet for managing notifications
#     """
#     serializer_class = NotificationSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['category', 'priority', 'is_read', 'type']
#     search_fields = ['title', 'message']
#     ordering_fields = ['created_at', 'priority']
#     ordering = ['-created_at']

#     def get_queryset(self):
#         """
#         Get notifications for the current user
#         """
#         user = self.request.user
#         queryset = Notification.objects.filter(user=user)
#         
#         # Apply date filters
#         date_from = self.request.query_params.get('date_from')
#         date_to = self.request.query_params.get('date_to')
#         
#         if date_from:
#             queryset = queryset.filter(created_at__date__gte=date_from)
#         if date_to:
#             queryset = queryset.filter(created_at__date__lte=date_to)
#         
#         return queryset


# class CartView(APIView):
#     """Cart management view"""
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get(self, request):
#         """Get user's cart"""
#         try:
#             # Get cart items for authenticated user
#             cart_items = CartItem.objects.filter(user=request.user).select_related(
#                 'product', 'material', 'wilaya', 'applied_coupon'
#             ).order_by('-created_at')
            
#             # Serialize with computed fields
#             serializer = CartItemSerializer(cart_items, many=True)
            
#             # Calculate cart summary
#             cart_summary = self.calculate_cart_summary(cart_items)
            
#             return Response({
#                 'items': serializer.data,
#                 'summary': cart_summary,
#                 'wilaya': ShippingSerializer(cart_items.first().wilaya).data if cart_items.first() and cart_items.first().wilaya else None,
#                 'delivery_type': cart_items.first().delivery_type if cart_items.first() else 'home'
#             })
            
#         except Exception as e:
#             return Response(
#                 {'error': str(e)}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
    def post(self, request):
        """Add item to cart"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'product_id' not in data:
                return Response(
                    {'error': 'Product ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product = Product.objects.get(id=data['product_id'])
            
            # Check product availability
            if not product.is_active:
                return Response(
                    {'error': 'Product is not available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            quantity = data.get('quantity', 1)
            if product.stock < quantity:
                return Response(
                    {'error': f'Only {product.stock} items available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get material if specified
            material = None
            if data.get('material_id'):
                material = Material.objects.get(id=data['material_id'])
            
            # Get wilaya if specified
            wilaya = None
            if data.get('wilaya_id'):
                wilaya = Shipping.objects.get(wilaya_id=data['wilaya_id'])
                if not wilaya.is_active:
                    return Response(
                        {'error': 'Shipping to this wilaya is not available'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                material=material,
                width=data.get('width'),
                height=data.get('height'),
                defaults={
                    'quantity': quantity,
                    'dimension_unit': data.get('dimension_unit', 'cm'),
                    'delivery_type': data.get('delivery_type', 'home'),
                    'wilaya': wilaya,
                    'options': data.get('options', {}),
                    'unit_price': product.base_price,
                    'material_price': material.price_per_m2 if material else 0,
                }
            )
            
            if not created:
                # Update existing item
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return Response(
                        {'error': f'Only {product.stock} items available'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                cart_item.quantity = new_quantity
                cart_item.save()
            
            # Calculate shipping cost
            if wilaya:
                cart_item.shipping_cost = cart_item.calculate_shipping_cost(
                    wilaya, data.get('delivery_type', 'home')
                )
                cart_item.save()
            
            # Get updated cart
            cart_items = CartItem.objects.filter(user=request.user).select_related(
                'product', 'material', 'wilaya', 'applied_coupon'
            )
            
            serializer = CartItemSerializer(cart_items, many=True)
            cart_summary = self.calculate_cart_summary(cart_items)
            
            return Response({
                'success': True,
                'message': 'Added to cart successfully',
                'cart_item': CartItemSerializer(cart_item).data,
                'cart_summary': cart_summary
            })
            
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Material.DoesNotExist:
            return Response(
                {'error': 'Material not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Shipping.DoesNotExist:
            return Response(
                {'error': 'Wilaya not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def calculate_cart_summary(self, cart_items):
        """Calculate cart summary"""
        if not cart_items:
            return {
                'total_items': 0,
                'subtotal': 0,
                'discount_total': 0,
                'shipping_cost': 0,
                'total': 0
            }
        
        subtotal = sum(item.subtotal for item in cart_items)
        discount_total = sum(
            (item.discount_amount or 0) + (item.coupon_discount or 0) 
            for item in cart_items
        )
        shipping_cost = sum(item.shipping_cost for item in cart_items)
        total = sum(item.final_total for item in cart_items)
        
        return {
            'total_items': cart_items.count(),
            'subtotal': float(subtotal),
            'discount_total': float(discount_total),
            'shipping_cost': float(shipping_cost),
            'total': float(total)
        }


class ClearCartView(APIView):
    """Clear user's cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        try:
            CartItem.objects.filter(user=request.user).delete()
            
            return Response({
                'success': True,
                'message': 'Cart cleared successfully'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MergeCartView(APIView):
    """Merge guest cart with user cart after login"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            
            if not session_id:
                return Response(
                    {'error': 'Session ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get guest cart items
            guest_items = CartItem.objects.filter(
                session_id=session_id,
                user__isnull=True
            ).select_related('product', 'material')
            
            # Move to user cart
            merged_count = 0
            for guest_item in guest_items:
                # Check if user already has similar item
                existing_item = CartItem.objects.filter(
                    user=request.user,
                    product=guest_item.product,
                    material=guest_item.material,
                    width=guest_item.width,
                    height=guest_item.height
                ).first()
                
                if existing_item:
                    # Merge quantities
                    existing_item.quantity += guest_item.quantity
                    existing_item.save()
                else:
                    # Move to user cart
                    guest_item.user = request.user
                    guest_item.session_id = None
                    guest_item.save()
                    merged_count += 1
            
            # Delete remaining guest items
            guest_items.delete()
            
            return Response({
                'success': True,
                'message': f'Merged {merged_count} items from guest cart',
                'merged_count': merged_count
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WilayasView(APIView):
    """Get all wilayas with shipping information"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            wilayas = Shipping.objects.all().order_by('wilaya_code')
            serializer = ShippingSerializer(wilayas, many=True)
            
            # Add statistics
            active_count = wilayas.filter(is_active=True).count()
            avg_home_price = wilayas.aggregate(
                avg=Sum('home_delivery_price')
            )['avg__sum'] or 0
            avg_stop_price = wilayas.aggregate(
                avg=Sum('stop_desk_price')
            )['avg__sum'] or 0
            
            return Response({
                'results': serializer.data,
                'count': wilayas.count(),
                'active_count': active_count,
                'statistics': {
                    'average_home_delivery_price': float(avg_home_price / active_count) if active_count > 0 else 0,
                    'average_stop_desk_price': float(avg_stop_price / active_count) if active_count > 0 else 0,
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WilayaDetailView(APIView):
    """Get specific wilaya details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, wilaya_id):
        try:
            wilaya = Shipping.objects.get(wilaya_id=wilaya_id)
            serializer = ShippingSerializer(wilaya)
            
            return Response(serializer.data)
            
        except Shipping.DoesNotExist:
            return Response(
                {'error': 'Wilaya not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, wilaya_id):
        """Update wilaya shipping prices (Admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin privileges required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            wilaya = Shipping.objects.get(wilaya_id=wilaya_id)
            data = json.loads(request.body)
            
            # Update allowed fields
            allowed_fields = [
                'home_delivery_price', 'stop_desk_price', 'express_delivery_price',
                'free_shipping_minimum', 'delivery_time_days', 'is_active'
            ]
            
            for field in allowed_fields:
                if field in data:
                    setattr(wilaya, field, data[field])
            
            wilaya.save()
            
            return Response({
                'success': True,
                'message': 'Wilaya updated successfully',
                'data': ShippingSerializer(wilaya).data
            })
            
        except Shipping.DoesNotExist:
            return Response(
                {'error': 'Wilaya not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkUpdateShippingView(APIView):
    """Bulk update shipping prices (Admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin privileges required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            data = json.loads(request.body)
            wilaya_ids = data.get('wilaya_ids', [])
            updates = data.get('updates', {})
            
            if not wilaya_ids:
                return Response(
                    {'error': 'Wilaya IDs are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            updated_count = 0
            errors = []
            
            for wilaya_id in wilaya_ids:
                try:
                    wilaya = Shipping.objects.get(wilaya_id=wilaya_id)
                    
                    # Update fields
                    for field, value in updates.items():
                        if hasattr(wilaya, field):
                            setattr(wilaya, field, value)
                    
                    wilaya.save()
                    updated_count += 1
                    
                except Shipping.DoesNotExist:
                    errors.append(f'Wilaya {wilaya_id} not found')
                except Exception as e:
                    errors.append(f'Error updating wilaya {wilaya_id}: {str(e)}')
            
            return Response({
                'success': True,
                'message': f'Updated {updated_count} wilayas successfully',
                'updated_count': updated_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalculateShippingView(APIView):
    """Calculate shipping cost for given parameters"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            wilaya_id = data.get('wilaya_id')
            delivery_type = data.get('delivery_type', 'home')
            order_weight = data.get('order_weight')
            order_volume = data.get('order_volume')
            order_total = data.get('order_total')
            
            if not wilaya_id:
                return Response(
                    {'error': 'Wilaya ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            wilaya = Shipping.objects.get(wilaya_id=wilaya_id)
            
            if not wilaya.is_active:
                return Response(
                    {'error': 'Shipping to this wilaya is not available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate base shipping cost
            base_cost = wilaya.get_delivery_price(delivery_type)
            
            # Additional charges
            additional_cost = 0
            
            if order_weight and order_weight > 10:
                additional_cost += (order_weight - 10) * 50  # 50 DZD per kg over 10kg
            
            if order_volume and order_volume > 0.1:
                additional_cost += (order_volume - 0.1) * 100  # 100 DZD per m³ over 0.1m³
            
            total_cost = base_cost + additional_cost
            
            # Check for free shipping
            is_free = wilaya.is_free_shipping_eligible(order_total or 0)
            
            # Calculate delivery time
            delivery_time = wilaya.delivery_time_days or 2
            if delivery_type == 'express':
                delivery_time = 1
            elif delivery_type == 'stop_desk':
                delivery_time = max(1, delivery_time - 1)
            
            return Response({
                'success': True,
                'shipping_cost': float(total_cost),
                'additional_cost': float(additional_cost),
                'is_free_shipping': is_free,
                'delivery_time_days': delivery_time,
                'delivery_type': delivery_type,
                'wilaya': ShippingSerializer(wilaya).data
            })
            
        except Shipping.DoesNotExist:
            return Response(
                {'error': 'Wilaya not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_coupon_to_cart(request):
    """Apply coupon to cart items"""
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code', '').upper()
        cart_item_ids = data.get('cart_item_ids', [])
        
        if not coupon_code:
            return Response(
                {'error': 'Coupon code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get and validate coupon
        coupon = Coupon.objects.get(
            code=coupon_code,
            is_active=True
        )
        
        # Check coupon validity
        now = timezone.now()
        if coupon.valid_from and coupon.valid_from > now:
            return Response(
                {'error': 'Coupon is not yet valid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if coupon.valid_to and coupon.valid_to < now:
            return Response(
                {'error': 'Coupon has expired'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart items to apply coupon to
        cart_items = CartItem.objects.filter(user=request.user)
        if cart_item_ids:
            cart_items = cart_items.filter(id__in=cart_item_ids)
        
        # Apply coupon to each item
        total_discount = 0
        for cart_item in cart_items:
            if coupon.discount_type == 'percentage':
                discount = cart_item.subtotal * (coupon.discount_value / 100)
            else:  # fixed amount
                discount = min(coupon.discount_value, cart_item.subtotal)
            
            cart_item.coupon_discount = discount
            cart_item.applied_coupon = coupon
            cart_item.save()
            total_discount += discount
        
        return Response({
            'success': True,
            'message': 'Coupon applied successfully',
            'total_discount': float(total_discount),
            'applied_items': len(cart_items)
        })
        
    except Coupon.DoesNotExist:
        return Response(
            {'error': 'Invalid coupon code'}, 
            status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_shipping_for_cart(request):
    """Set shipping information for cart"""
    try:
        data = json.loads(request.body)
        wilaya_id = data.get('wilaya_id')
        delivery_type = data.get('delivery_type', 'home')
        cart_item_ids = data.get('cart_item_ids', [])
        
        if not wilaya_id:
            return Response(
                {'error': 'Wilaya ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get wilaya
        wilaya = Shipping.objects.get(wilaya_id=wilaya_id)
        
        if not wilaya.is_active:
            return Response(
                {'error': 'Shipping to this wilaya is not available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart items to update
        cart_items = CartItem.objects.filter(user=request.user)
        if cart_item_ids:
            cart_items = cart_items.filter(id__in=cart_item_ids)
        
        # Update shipping for each item
        total_shipping = 0
        for cart_item in cart_items:
            cart_item.wilaya = wilaya
            cart_item.delivery_type = delivery_type
            cart_item.shipping_cost = cart_item.calculate_shipping_cost(wilaya, delivery_type)
            cart_item.save()
            total_shipping += cart_item.shipping_cost
        
        return Response({
            'success': True,
            'message': 'Shipping updated successfully',
            'total_shipping_cost': float(total_shipping),
            'updated_items': len(cart_items),
            'wilaya': ShippingSerializer(wilaya).data
        })
        
    except Shipping.DoesNotExist:
        return Response(
            {'error': 'Wilaya not found'}, 
            status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get unread notifications
        """
        unread_notifications = self.get_queryset().filter(is_read=False)
        page = self.paginate_queryset(unread_notifications)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read
        """
        notification_ids = request.data.get('notification_ids', [])
        
        if notification_ids:
            # Mark specific notifications as read
            notifications = self.get_queryset().filter(
                id__in=notification_ids,
                is_read=False
            )
            count = notifications.count()
            notifications.update(is_read=True, read_at=timezone.now())
        else:
            # Mark all notifications as read
            notifications = self.get_queryset().filter(is_read=False)
            count = notifications.count()
            notifications.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a specific notification as read
        """
        notification = self.get_object()
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear_all(self, request):
        """
        Clear all notifications for the user
        """
        count, _ = self.get_queryset().delete()
        
        return Response({
            'message': f'Cleared {count} notifications',
            'count': count
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get notification statistics for the user
        """
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'unread': queryset.filter(is_read=False).count(),
            'read': queryset.filter(is_read=True).count(),
            'by_category': queryset.values('category').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_priority': queryset.values('priority').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_type': queryset.values('type').annotate(
                count=Count('id')
            ).order_by('-count')[:10]  # Top 10 types
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent notifications (last 20)
        """
        recent_notifications = self.get_queryset()[:20]
        serializer = self.get_serializer(recent_notifications, many=True)
        return Response(serializer.data)


class AdminBroadcastView(APIView):
    """
    Admin-only view for sending broadcast notifications
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """
        Send a broadcast notification
        """
        data = request.data
        
        # Validate required fields
        required_fields = ['title', 'message', 'recipient_type']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # Create broadcast notification
            notification = NotificationEngine.create_notification(
                notification_type=data.get('type', 'system_update'),
                title=data['title'],
                message=data['message'],
                recipient_type=data['recipient_type'],
                priority=data.get('priority', 'medium'),
                category=data.get('category', 'system'),
                metadata=data.get('metadata', {}),
                action_url=data.get('action_url'),
                action_text=data.get('action_text'),
                sender='admin',
                recipient_group=data.get('recipient_group')
            )
            
            # Handle scheduled notifications
            if data.get('schedule_at'):
                from datetime import datetime
                schedule_time = datetime.fromisoformat(data['schedule_at'])
                notification.metadata['schedule_at'] = schedule_time.isoformat()
                notification.metadata['sent'] = False
                notification.save(update_fields=['metadata'])
            
            return Response({
                'message': 'Broadcast sent successfully',
                'notification_id': notification.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """
        Get broadcast statistics and options
        """
        # Get available groups
        from django.contrib.auth.models import Group
        groups = Group.objects.all().values('id', 'name')
        
        # Get recent broadcasts
        recent_broadcasts = Notification.objects.filter(
            recipient_type__in=['all', 'group'],
            sender='admin'
        ).order_by('-created_at')[:10]
        
        serializer = NotificationSerializer(recent_broadcasts, many=True)
        
        return Response({
            'groups': list(groups),
            'recent_broadcasts': serializer.data,
            'statistics': {
                'total_broadcasts': Notification.objects.filter(
                    recipient_type__in=['all', 'group'],
                    sender='admin'
                ).count(),
                'recent_broadcasts_24h': Notification.objects.filter(
                    recipient_type__in=['all', 'group'],
                    sender='admin',
                    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
                ).count()
            }
        })


class NotificationPreferencesView(APIView):
    """
    View for managing user notification preferences
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get user notification preferences
        """
        user = request.user
        preferences = user.profile.preferences.get('notifications', {})
        
        return Response({
            'preferences': preferences,
            'default_preferences': {
                'email_notifications': True,
                'push_notifications': True,
                'sms_notifications': False,
                'categories': {
                    'order': True,
                    'finance': True,
                    'marketing': False,
                    'system': True,
                    'security': True
                }
            }
        })

    def post(self, request):
        """
        Update user notification preferences
        """
        user = request.user
        preferences = request.data.get('preferences', {})
        
        # Validate preferences
        valid_categories = ['order', 'finance', 'marketing', 'system', 'security', 'logistics', 'inventory', 'customer_service']
        
        if 'categories' in preferences:
            for category in preferences['categories']:
                if category not in valid_categories:
                    return Response(
                        {'error': f'Invalid category: {category}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Update user preferences
        user.profile.preferences['notifications'] = preferences
        user.profile.save(update_fields=['preferences'])
        
        return Response({
            'message': 'Preferences updated successfully',
            'preferences': preferences
        })


class NotificationSearchView(APIView):
    """
    Advanced search for notifications
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Search notifications with advanced filters
        """
        user = request.user
        data = request.data
        
        # Build queryset
        queryset = Notification.objects.filter(user=user)
        
        # Text search
        if data.get('search'):
            search_term = data['search']
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(message__icontains=search_term)
            )
        
        # Category filter
        if data.get('categories'):
            queryset = queryset.filter(category__in=data['categories'])
        
        # Priority filter
        if data.get('priorities'):
            queryset = queryset.filter(priority__in=data['priorities'])
        
        # Type filter
        if data.get('types'):
            queryset = queryset.filter(type__in=data['types'])
        
        # Date range
        if data.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=data['date_from'])
        if data.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=data['date_to'])
        
        # Read status
        if data.get('is_read') is not None:
            queryset = queryset.filter(is_read=data['is_read'])
        
        # Ordering
        ordering = data.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        # Pagination
        page_size = data.get('page_size', 20)
        page = data.get('page', 1)
        
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        notifications = queryset[start:end]
        
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })


class NotificationCountView(APIView):
    """
    Get notification counts for badges and indicators
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get various notification counts
        """
        user = request.user
        
        # Basic counts
        total_count = Notification.objects.filter(user=user).count()
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        
        # Priority counts
        high_priority_count = Notification.objects.filter(
            user=user,
            is_read=False,
            priority__in=['high', 'critical']
        ).count()
        
        # Category counts
        category_counts = Notification.objects.filter(
            user=user,
            is_read=False
        ).values('category').annotate(count=Count('id'))
        
        # Recent count (last 24 hours)
        recent_count = Notification.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).count()
        
        return Response({
            'total': total_count,
            'unread': unread_count,
            'high_priority': high_priority_count,
            'recent': recent_count,
            'by_category': list(category_counts)
        })


class HealthView(APIView):
    """Health check endpoint for monitoring"""
    
    def get(self, request):
        """Return health status"""
        return Response({
            'status': 'healthy',
            'service': 'VynilArt API',
            'version': '2.0.1',
            'timestamp': timezone.now().isoformat()
        })
