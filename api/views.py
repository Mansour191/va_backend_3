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


class HealthView(APIView):
    """Health check endpoint for monitoring"""
    
    def get(self, request):
        """Return health status"""
        return Response({
            'status': 'healthy',
            'service': 'VynilArt API',
            'version': '2.0.1',
            'timestamp': timezone.now().isoformat(),
            'message': 'REST API disabled - use GraphQL endpoints',
            'graphql_endpoints': {
                'graphql': '/api/graphql/',
                'graphql_batch': '/api/graphql/batch/'
            }
        })
