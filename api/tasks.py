"""
Celery Tasks for Background Forecasting Operations
Optimized for Core 2 Duo processors with memory efficiency
"""
import time
import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from api.models.analytics_new import Forecast, Product
from decimal import Decimal
import gc

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_product_forecast(self, product_id, algorithm='prophet', days=30):
    """
    Generate forecast for a specific product asynchronously
    Optimized for background execution on Core 2 Duo
    """
    try:
        logger.info(f'Starting forecast for product {product_id} using {algorithm}')
        
        # Get product
        product = Product.objects.get(id=product_id, is_active=True)
        
        # Generate forecast data
        forecast_data = _generate_forecast_data(product, algorithm, days)
        
        if forecast_data:
            # Save forecast in transaction
            with transaction.atomic():
                # Delete previous demand forecasts for this product
                Forecast.objects.filter(
                    product=product,
                    forecast_type='demand'
                ).delete()
                
                # Create new forecast
                Forecast.objects.create(**forecast_data)
            
            logger.info(f'Forecast generated successfully for product {product_id}')
            return {
                'success': True,
                'product_id': product_id,
                'predicted_demand': forecast_data['predicted_demand'],
                'algorithm': algorithm
            }
        else:
            logger.warning(f'Insufficient data for product {product_id}')
            return {
                'success': False,
                'product_id': product_id,
                'error': 'Insufficient historical data'
            }
            
    except Product.DoesNotExist:
        logger.error(f'Product {product_id} not found')
        return {
            'success': False,
            'product_id': product_id,
            'error': 'Product not found'
        }
    except Exception as exc:
        logger.error(f'Error generating forecast for product {product_id}: {str(exc)}')
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            logger.info(f'Retrying forecast for product {product_id} in {countdown} seconds')
            raise self.retry(countdown=countdown)
        
        return {
            'success': False,
            'product_id': product_id,
            'error': str(exc)
        }

@shared_task(bind=True)
def batch_forecast_products(self, product_ids, algorithm='prophet', days=30, batch_size=5):
    """
    Generate forecasts for multiple products in batches
    Memory optimized for Core 2 Duo processors
    """
    try:
        logger.info(f'Starting batch forecast for {len(product_ids)} products')
        
        results = []
        failed_products = []
        
        # Process products in small batches to manage memory
        for i in range(0, len(product_ids), batch_size):
            batch_ids = product_ids[i:i + batch_size]
            batch_number = i // batch_size + 1
            
            logger.info(f'Processing batch {batch_number}: products {i+1}-{min(i+batch_size, len(product_ids))}')
            
            # Process each product in batch
            for product_id in batch_ids:
                try:
                    result = generate_product_forecast(product_id, algorithm, days)
                    results.append(result)
                    
                    if not result.get('success'):
                        failed_products.append(product_id)
                    
                    # Small delay to prevent CPU overload
                    time.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f'Error in batch processing product {product_id}: {str(e)}')
                    failed_products.append(product_id)
            
            # Memory optimization between batches
            gc.collect()
            
            # Small delay between batches
            time.sleep(0.2)
        
        successful_count = len([r for r in results if r.get('success')])
        
        logger.info(f'Batch forecast completed: {successful_count}/{len(product_ids)} successful')
        
        return {
            'success': True,
            'total_products': len(product_ids),
            'successful': successful_count,
            'failed': len(failed_products),
            'failed_products': failed_products,
            'results': results
        }
        
    except Exception as exc:
        logger.error(f'Error in batch forecasting: {str(exc)}')
        
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown)
        
        return {
            'success': False,
            'error': str(exc)
        }

@shared_task
def update_forecast_accuracy(self, forecast_id, actual_demand):
    """
    Update forecast with actual demand and calculate error margin
    """
    try:
        with transaction.atomic():
            forecast = Forecast.objects.get(id=forecast_id)
            
            if forecast.predicted_demand and forecast.predicted_demand > 0:
                # Calculate error margin
                error_margin = abs((actual_demand - forecast.predicted_demand) / forecast.predicted_demand * 100)
                forecast.actual_demand = actual_demand
                forecast.error_margin = round(error_margin, 2)
                forecast.save()
                
                logger.info(f'Updated forecast {forecast_id} accuracy: {error_margin:.2f}%')
                
                return {
                    'success': True,
                    'forecast_id': forecast_id,
                    'error_margin': error_margin
                }
            else:
                logger.warning(f'Cannot calculate accuracy for forecast {forecast_id}: no predicted demand')
                return {
                    'success': False,
                    'forecast_id': forecast_id,
                    'error': 'No predicted demand available'
                }
                
    except Forecast.DoesNotExist:
        logger.error(f'Forecast {forecast_id} not found')
        return {
            'success': False,
            'forecast_id': forecast_id,
            'error': 'Forecast not found'
        }
    except Exception as exc:
        logger.error(f'Error updating forecast accuracy: {str(exc)}')
        return {
            'success': False,
            'forecast_id': forecast_id,
            'error': str(exc)
        }

@shared_task
def cleanup_old_forecasts(self, days_old=90):
    """
    Clean up old forecast data to manage database size
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        with transaction.atomic():
            deleted_count = Forecast.objects.filter(
                created_at__lt=cutoff_date
            ).delete()[0]
            
        logger.info(f'Cleaned up {deleted_count} old forecasts older than {days_old} days')
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        logger.error(f'Error cleaning up old forecasts: {str(exc)}')
        return {
            'success': False,
            'error': str(exc)
        }

def _generate_forecast_data(product, algorithm, days):
    """
    Generate forecast data for a product
    Memory optimized implementation
    """
    try:
        # Get historical sales (optimized for memory)
        historical_sales = _get_historical_sales(product.id, days=90)
        
        if not historical_sales or len(historical_sales) < 7:
            return None

        # Generate forecast using optimized algorithm
        predicted_demand = _simple_forecast(historical_sales, days)
        confidence = _calculate_confidence(historical_sales, predicted_demand)

        return {
            'product': product,
            'forecast_type': 'demand',
            'period': f'{days}days',
            'predicted_demand': predicted_demand,
            'algorithm_used': algorithm.upper(),
            'confidence': confidence,
            'created_at': timezone.now()
        }
        
    except Exception as e:
        logger.error(f'Error generating forecast data for product {product.id}: {str(e)}')
        return None

def _get_historical_sales(product_id, days=90):
    """
    Get historical sales data with memory optimization
    """
    try:
        # Mock implementation - replace with actual database query
        import random
        
        # Generate realistic mock data with memory efficiency
        base_demand = random.randint(50, 200)
        trend = random.uniform(-0.1, 0.15)
        
        sales_data = []
        for day in range(min(days, 90)):
            # Memory efficient calculation
            demand = base_demand * (1 + trend * day/90)
            demand += random.uniform(-demand*0.2, demand*0.2)
            sales_data.append(max(0, int(demand)))
        
        return sales_data
        
    except Exception as e:
        logger.error(f'Error getting historical sales for product {product_id}: {str(e)}')
        return []

def _simple_forecast(historical_sales, days):
    """
    Simple forecasting algorithm optimized for speed
    """
    if not historical_sales:
        return 0

    # Memory efficient moving average
    window_size = min(7, len(historical_sales))
    recent_avg = sum(historical_sales[-window_size:]) / window_size

    # Calculate trend
    if len(historical_sales) >= 14:
        old_avg = sum(historical_sales[-14:-7]) / 7
        trend = (recent_avg - old_avg) / old_avg if old_avg > 0 else 0
    else:
        trend = 0

    # Apply trend to forecast
    forecast = recent_avg * (1 + trend * days / 30)
    return max(0, int(forecast))

def _calculate_confidence(historical_sales, predicted_demand):
    """
    Calculate confidence score with memory optimization
    """
    if not historical_sales or len(historical_sales) < 7:
        return Decimal('50.00')

    # Calculate volatility efficiently
    avg_demand = sum(historical_sales[-7:]) / 7
    variance = sum((x - avg_demand) ** 2 for x in historical_sales[-7:]) / 7
    std_dev = variance ** 0.5

    # Confidence inversely proportional to volatility
    if avg_demand > 0:
        confidence = max(0, min(100, 100 - (std_dev / avg_demand * 100)))
    else:
        confidence = 50

    return Decimal(str(round(confidence, 2)))
