"""
Real Forecast Implementation - Connects to actual Order/OrderItem data
This replaces the mock data implementation with real database queries
"""
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Avg, Count
from .order import OrderItem, Order
from .product import Product
import logging

logger = logging.getLogger(__name__)

class RealForecastEngine:
    """
    Real forecast engine that pulls actual sales data from Order/OrderItem tables
    Enhanced with caching and seasonality logic
    """
    
    CACHE_TIMEOUT = 6 * 60 * 60  # 6 hours in seconds
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_historical_sales(self, product_id, days=90):
        """
        Get REAL historical sales data from OrderItem table with caching
        This is the ACTUAL function that connects to database
        """
        cache_key = f'forecast_sales_{product_id}_{days}'
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            self.logger.info(f'Using cached sales data for product {product_id}')
            return cached_data
        
        try:
            # Calculate date range
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # REAL DATABASE QUERY - pulls from OrderItem table
            sales_data = OrderItem.objects.filter(
                product_id=product_id,
                order__created_at__gte=start_date,
                order__created_at__lte=end_date,
                order__status__in=['completed', 'delivered', 'processing']  # Only valid orders
            ).extra(
                select={'day': 'DATE(order.created_at)'}
            ).values('day').annotate(
                daily_quantity=Sum('quantity'),
                daily_amount=Sum('price')
            ).order_by('day')
            
            # Convert to list format for forecast algorithm
            historical_sales = []
            for day_data in sales_data:
                if day_data['daily_quantity']:
                    historical_sales.append(int(day_data['daily_quantity']))
                else:
                    historical_sales.append(0)
            
            # Cache the result for 6 hours
            cache.set(cache_key, historical_sales, self.CACHE_TIMEOUT)
            
            self.logger.info(f'Pulled and cached {len(historical_sales)} days of real sales data for product {product_id}')
            
            return historical_sales
            
        except Exception as e:
            self.logger.error(f'Error getting real historical sales for product {product_id}: {str(e)}')
            return []
    
    def calculate_forecast(self, product_id, forecast_days=30):
        """
        Calculate forecast using REAL data with caching and seasonality logic
        """
        cache_key = f'forecast_result_{product_id}_{forecast_days}'
        
        # Try to get from cache first
        cached_forecast = cache.get(cache_key)
        if cached_forecast is not None:
            self.logger.info(f'Using cached forecast for product {product_id}')
            return cached_forecast
        
        try:
            # Get REAL historical data
            historical_sales = self.get_historical_sales(product_id, days=90)
            
            if not historical_sales or len(historical_sales) < 7:
                self.logger.warning(f'Insufficient real data for product {product_id}')
                return None
            
            # Apply enhanced forecast algorithm with seasonality
            predicted_demand = self._seasonal_forecast(historical_sales, forecast_days)
            confidence = self._calculate_confidence(historical_sales, predicted_demand)
            
            # Get product info
            product = Product.objects.get(id=product_id)
            
            forecast_data = {
                'product': product,
                'forecast_type': 'demand',
                'period': f'{forecast_days}days',
                'predicted_demand': predicted_demand,
                'algorithm_used': 'SEASONAL_REAL_DATA',
                'confidence': confidence,
                'data_source': 'OrderItem Table',
                'historical_data_points': len(historical_sales),
                'seasonality_applied': True,
                'created_at': timezone.now()
            }
            
            # Cache the forecast result for 6 hours
            cache.set(cache_key, forecast_data, self.CACHE_TIMEOUT)
            
            self.logger.info(f'Calculated and cached forecast for product {product_id}')
            
            return forecast_data
            
        except Exception as e:
            self.logger.error(f'Error calculating real forecast for product {product_id}: {str(e)}')
            return None
    
    def _simple_forecast(self, historical_sales, days):
        """
        Mathematical forecast formula using REAL data
        Formula: forecast = recent_avg * (1 + trend * days/30)
        """
        if not historical_sales:
            return 0
        
        # Calculate moving average (last 7 days)
        window_size = min(7, len(historical_sales))
        recent_avg = sum(historical_sales[-window_size:]) / window_size
        
        # Calculate trend (compare last 7 days with previous 7 days)
        if len(historical_sales) >= 14:
            old_avg = sum(historical_sales[-14:-7]) / 7
            trend = (recent_avg - old_avg) / old_avg if old_avg > 0 else 0
        else:
            trend = 0
        
        # Apply mathematical formula
        forecast = recent_avg * (1 + trend * days / 30)
        
        return max(0, int(forecast))
    
    def _seasonal_forecast(self, historical_sales, days):
        """
        Enhanced forecast with seasonality logic using day-of-week patterns
        Formula: forecast = recent_avg * (1 + trend * days/30) * seasonality_factor
        """
        if not historical_sales:
            return 0
        
        # Calculate basic forecast first
        base_forecast = self._simple_forecast(historical_sales, days)
        
        # Calculate day-of-week seasonality factors
        seasonality_factors = self._calculate_day_of_week_seasonality(historical_sales)
        
        # Get current day of week (0=Monday, 6=Sunday)
        current_day = timezone.now().weekday()
        
        # Apply seasonality factor based on current day
        seasonality_factor = seasonality_factors.get(current_day, 1.0)
        
        # Apply seasonality to base forecast
        seasonal_forecast = base_forecast * seasonality_factor
        
        self.logger.info(f'Seasonality factor for day {current_day}: {seasonality_factor:.2f}')
        
        return max(0, int(seasonal_forecast))
    
    def _calculate_day_of_week_seasonality(self, historical_sales):
        """
        Calculate seasonality factors for each day of the week
        Based on average sales patterns for each day
        """
        if len(historical_sales) < 14:  # Need at least 2 weeks for seasonality
            return {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0}
        
        # Calculate average sales for each day of week
        day_sales = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}  # Monday to Sunday
        
        # Get sales data with dates for seasonality calculation
        end_date = timezone.now()
        start_date = end_date - timedelta(days=len(historical_sales))
        
        try:
            sales_with_dates = OrderItem.objects.filter(
                product_id=self.product_id if hasattr(self, 'product_id') else None,
                order__created_at__gte=start_date,
                order__created_at__lte=end_date,
                order__status__in=['completed', 'delivered', 'processing']
            ).extra(
                select={'day': 'DATE(order.created_at)', 'weekday': 'DAYOFWEEK(order.created_at)'}
            ).values('weekday').annotate(
                daily_quantity=Sum('quantity')
            ).order_by('day')
            
            # Group by weekday (MySQL DAYOFWEEK: 1=Sunday, 2=Monday, ..., 7=Saturday)
            for sale in sales_with_dates:
                mysql_weekday = sale['weekday'] - 1  # Convert to Python weekday (0=Monday)
                if mysql_weekday < 0:
                    mysql_weekday = 6  # Sunday becomes 6
                
                if sale['daily_quantity']:
                    day_sales[mysql_weekday].append(int(sale['daily_quantity']))
            
        except Exception as e:
            self.logger.warning(f'Could not calculate detailed seasonality: {str(e)}')
            # Fallback: use historical sales pattern
            for i, sales in enumerate(historical_sales):
                day_of_week = (timezone.now() - timedelta(days=len(historical_sales) - i)).weekday()
                day_sales[day_of_week].append(sales)
        
        # Calculate average for each day of week
        day_averages = {}
        overall_avg = sum(historical_sales) / len(historical_sales)
        
        for day, sales in day_sales.items():
            if sales:
                day_avg = sum(sales) / len(sales)
                # Seasonality factor = day average / overall average
                day_averages[day] = day_avg / overall_avg if overall_avg > 0 else 1.0
            else:
                day_averages[day] = 1.0
        
        return day_averages
    
    def _calculate_confidence(self, historical_sales, predicted_demand):
        """
        Calculate confidence based on data volatility
        Formula: confidence = max(0, min(100, 100 - (std_dev / avg_demand * 100)))
        """
        if not historical_sales or len(historical_sales) < 7:
            return Decimal('50.00')
        
        # Calculate statistical measures
        avg_demand = sum(historical_sales[-7:]) / 7
        variance = sum((x - avg_demand) ** 2 for x in historical_sales[-7:]) / 7
        std_dev = variance ** 0.5
        
        # Confidence calculation
        if avg_demand > 0:
            confidence = max(0, min(100, 100 - (std_dev / avg_demand * 100)))
        else:
            confidence = 50
        
        return Decimal(str(round(confidence, 2)))
    
    def validate_data_integrity(self, product_id):
        """
        Validate that we have real data and not mock data
        """
        try:
            # Check if we have actual order items
            order_count = OrderItem.objects.filter(
                product_id=product_id,
                order__status__in=['completed', 'delivered', 'processing']
            ).count()
            
            if order_count == 0:
                self.logger.warning(f'No real orders found for product {product_id}')
                return False, "No real orders found"
            
            # Check date range of data
            oldest_order = OrderItem.objects.filter(
                product_id=product_id
            ).order_by('order__created_at').first()
            
            newest_order = OrderItem.objects.filter(
                product_id=product_id
            ).order_by('-order__created_at').first()
            
            data_range = {
                'order_count': order_count,
                'oldest_order': oldest_order.order.created_at if oldest_order else None,
                'newest_order': newest_order.order.created_at if newest_order else None,
                'data_span_days': (newest_order.order.created_at - oldest_order.order.created_at).days if oldest_order and newest_order else 0
            }
            
            return True, data_range
            
        except Exception as e:
            self.logger.error(f'Error validating data integrity for product {product_id}: {str(e)}')
            return False, str(e)
