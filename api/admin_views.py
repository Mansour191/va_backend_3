"""
Admin Views for Shipping Methods Management
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.utils import timezone

from core.models import ShippingMethod, ShippingPrice, Shipping
from core.serializers import (
    ShippingMethodSerializer, 
    ShippingPriceSerializer,
    ShippingPriceCreateSerializer,
    ShippingWithPricesSerializer
)


class ShippingMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shipping methods
    """
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['provider', 'service_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['provider', 'service_type', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get shipping methods with usage statistics
        """
        queryset = ShippingMethod.objects.all()
        
        # Add usage statistics
        queryset = queryset.annotate(
            total_prices=Count('prices'),
            active_prices=Count('prices', filter=Q(prices__is_active=True))
        )
        
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """
        Bulk activate/deactivate shipping methods
        """
        try:
            data = request.data
            method_ids = data.get('method_ids', [])
            is_active = data.get('is_active', True)
            
            updated_count = ShippingMethod.objects.filter(
                id__in=method_ids
            ).update(is_active=is_active)
            
            return Response({
                'success': True,
                'message': f'{"Activated" if is_active else "Deactivated"} {updated_count} shipping methods',
                'updated_count': updated_count
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a shipping method
        """
        try:
            original_method = self.get_object()
            
            # Create duplicate
            new_method = ShippingMethod.objects.create(
                name=f"{original_method.name} (Copy)",
                provider=original_method.provider,
                service_type=original_method.service_type,
                expected_delivery_time=original_method.expected_delivery_time,
                description=original_method.description,
                is_active=False,  # Start as inactive
                tracking_url_template=original_method.tracking_url_template,
                api_endpoint=original_method.api_endpoint,
                # Don't copy API key for security
            )
            
            # Copy prices if requested
            copy_prices = request.data.get('copy_prices', False)
            if copy_prices:
                original_prices = ShippingPrice.objects.filter(
                    shipping_method=original_method
                )
                
                for price in original_prices:
                    ShippingPrice.objects.create(
                        wilaya=price.wilaya,
                        shipping_method=new_method,
                        home_delivery_price=price.home_delivery_price,
                        stop_desk_price=price.stop_desk_price,
                        express_price=price.express_price,
                        free_shipping_minimum=price.free_shipping_minimum,
                        weight_surcharge=price.weight_surcharge,
                        volume_surcharge=price.volume_surcharge,
                        cod_available=price.cod_available,
                        insurance_available=price.insurance_available,
                        tracking_available=price.tracking_available,
                        is_active=False  # Start as inactive
                    )
            
            serializer = self.get_serializer_class()(new_method)
            return Response({
                'success': True,
                'message': 'Shipping method duplicated successfully',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get shipping methods statistics
        """
        try:
            stats = {}
            
            # Provider statistics
            provider_stats = ShippingMethod.objects.values('provider').annotate(
                count=Count('id'),
                active_count=Count('id', filter=Q(is_active=True))
            )
            stats['by_provider'] = list(provider_stats)
            
            # Service type statistics
            service_stats = ShippingMethod.objects.values('service_type').annotate(
                count=Count('id'),
                active_count=Count('id', filter=Q(is_active=True))
            )
            stats['by_service_type'] = list(service_stats)
            
            # Overall statistics
            stats['total'] = ShippingMethod.objects.count()
            stats['active'] = ShippingMethod.objects.filter(is_active=True).count()
            stats['inactive'] = ShippingMethod.objects.filter(is_active=False).count()
            
            # Most used providers (based on price configurations)
            most_used = ShippingMethod.objects.annotate(
                price_count=Count('prices')
            ).order_by('-price_count')[:5]
            stats['most_used'] = [
                {
                    'id': method.id,
                    'name': method.name,
                    'price_count': method.price_count
                }
                for method in most_used
            ]
            
            return Response({
                'success': True,
                'data': stats
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShippingPriceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shipping prices
    """
    serializer_class = ShippingPriceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'wilaya', 'shipping_method', 'is_active',
        'shipping_method__provider', 'shipping_method__service_type'
    ]
    search_fields = [
        'wilaya__name_ar', 'wilaya__name_en', 
        'shipping_method__name', 'shipping_method__provider'
    ]
    ordering_fields = [
        'wilaya__wilaya_code', 'shipping_method__provider', 
        'home_delivery_price', 'stop_desk_price', 'created_at'
    ]
    ordering = ['wilaya__wilaya_code', 'shipping_method__provider']

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ShippingPriceCreateSerializer
        return ShippingPriceSerializer

    def get_queryset(self):
        """
        Get shipping prices with related data
        """
        return ShippingPrice.objects.select_related(
            'wilaya', 'shipping_method'
        ).all()

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update shipping prices
        """
        try:
            data = request.data
            wilaya_ids = data.get('wilaya_ids', [])
            updates = data.get('updates', {})
            
            if not wilaya_ids:
                return Response({
                    'success': False,
                    'error': 'Wilaya IDs are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            updated_count = 0
            errors = []
            
            for wilaya_id in wilaya_ids:
                try:
                    # Get existing prices for this wilaya
                    existing_prices = ShippingPrice.objects.filter(
                        wilaya_id=wilaya_id
                    )
                    
                    # Update or create prices
                    for method_id, price_data in updates.get('method_prices', {}).items():
                        try:
                            shipping_method = ShippingMethod.objects.get(id=method_id)
                            
                            price, created = ShippingPrice.objects.update_or_create(
                                wilaya_id=wilaya_id,
                                shipping_method_id=method_id,
                                defaults={
                                    'home_delivery_price': price_data.get('home_delivery_price', 0),
                                    'stop_desk_price': price_data.get('stop_desk_price', 0),
                                    'express_price': price_data.get('express_price'),
                                    'free_shipping_minimum': price_data.get('free_shipping_minimum'),
                                    'weight_surcharge': price_data.get('weight_surcharge', 0),
                                    'volume_surcharge': price_data.get('volume_surcharge', 0),
                                    'cod_available': price_data.get('cod_available', True),
                                    'insurance_available': price_data.get('insurance_available', False),
                                    'tracking_available': price_data.get('tracking_available', True),
                                    'is_active': price_data.get('is_active', True)
                                }
                            )
                            
                            if not created:
                                # Update existing
                                for field, value in price_data.items():
                                    if hasattr(price, field):
                                        setattr(price, field, value)
                                price.save()
                            
                            updated_count += 1
                            
                        except ShippingMethod.DoesNotExist:
                            errors.append(f'Shipping method {method_id} not found')
                        except Exception as e:
                            errors.append(f'Error updating wilaya {wilaya_id}, method {method_id}: {str(e)}')
                
                except Exception as e:
                    errors.append(f'Error processing wilaya {wilaya_id}: {str(e)}')
            
            return Response({
                'success': len(errors) == 0,
                'message': f'Updated {updated_count} shipping prices successfully',
                'updated_count': updated_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def copy_prices(self, request):
        """
        Copy prices from one shipping method to another
        """
        try:
            data = request.data
            source_method_id = data.get('source_method_id')
            target_method_id = data.get('target_method_id')
            wilaya_ids = data.get('wilaya_ids', [])
            
            if not source_method_id or not target_method_id:
                return Response({
                    'success': False,
                    'error': 'Source and target method IDs are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get source prices
            source_prices = ShippingPrice.objects.filter(
                shipping_method_id=source_method_id
            )
            
            if wilaya_ids:
                source_prices = source_prices.filter(wilaya_id__in=wilaya_ids)
            
            copied_count = 0
            for source_price in source_prices:
                try:
                    # Create or update target price
                    ShippingPrice.objects.update_or_create(
                        wilaya=source_price.wilaya,
                        shipping_method_id=target_method_id,
                        defaults={
                            'home_delivery_price': source_price.home_delivery_price,
                            'stop_desk_price': source_price.stop_desk_price,
                            'express_price': source_price.express_price,
                            'free_shipping_minimum': source_price.free_shipping_minimum,
                            'weight_surcharge': source_price.weight_surcharge,
                            'volume_surcharge': source_price.volume_surcharge,
                            'cod_available': source_price.cod_available,
                            'insurance_available': source_price.insurance_available,
                            'tracking_available': source_price.tracking_available,
                            'is_active': False  # Start as inactive for review
                        }
                    )
                    copied_count += 1
                    
                except Exception as e:
                    continue
            
            return Response({
                'success': True,
                'message': f'Copied {copied_count} prices successfully',
                'copied_count': copied_count
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def price_matrix(self, request):
        """
        Get price matrix for all wilayas and methods
        """
        try:
            # Get all active shipping methods
            methods = ShippingMethod.objects.filter(is_active=True)
            
            # Get all active wilayas
            wilayas = Shipping.objects.filter(is_active=True).order_by('wilaya_code')
            
            # Build matrix
            matrix = {}
            for wilaya in wilayas:
                matrix[wilaya.wilaya_code] = {
                    'wilaya_id': wilaya.id,
                    'wilaya_name': wilaya.name_ar,
                    'methods': {}
                }
                
                for method in methods:
                    try:
                        price = ShippingPrice.objects.get(
                            wilaya=wilaya,
                            shipping_method=method,
                            is_active=True
                        )
                        
                        matrix[wilaya.wilaya_code]['methods'][method.id] = {
                            'method_id': method.id,
                            'method_name': method.name,
                            'provider': method.provider,
                            'service_type': method.service_type,
                            'home_price': float(price.home_delivery_price),
                            'desk_price': float(price.stop_desk_price),
                            'express_price': float(price.express_price) if price.express_price else None,
                            'free_shipping_minimum': float(price.free_shipping_minimum) if price.free_shipping_minimum else None
                        }
                        
                    except ShippingPrice.DoesNotExist:
                        # No price configured
                        matrix[wilaya.wilaya_code]['methods'][method.id] = {
                            'method_id': method.id,
                            'method_name': method.name,
                            'provider': method.provider,
                            'service_type': method.service_type,
                            'home_price': None,
                            'desk_price': None,
                            'express_price': None,
                            'free_shipping_minimum': None
                        }
            
            return Response({
                'success': True,
                'data': matrix
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
