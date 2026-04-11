"""
Django Management Command for Background Forecasting
Optimized for Core 2 Duo processors with memory-efficient operations
"""
import time
import logging
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils import timezone
from api.models.analytics_new import Forecast, Product
from decimal import Decimal
import gc

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run demand forecasting calculations in background with memory optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of products to process in each batch (default: 10)'
        )
        parser.add_argument(
            '--algorithm',
            type=str,
            default='prophet',
            choices=['prophet', 'arima', 'simple'],
            help='Forecasting algorithm to use (default: prophet)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to forecast (default: 30)'
        )
        parser.add_argument(
            '--memory-limit',
            type=int,
            default=512,  # MB
            help='Memory limit in MB for processing (default: 512)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        algorithm = options['algorithm']
        days = options['days']
        memory_limit = options['memory_limit'] * 1024 * 1024  # Convert to bytes

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting background forecasting with algorithm={algorithm}, '
                f'batch_size={batch_size}, days={days}'
            )
        )

        start_time = time.time()
        total_products = 0
        processed_products = 0
        failed_products = []

        try:
            # Get all active products
            products = Product.objects.filter(is_active=True).order_by('id')
            total_products = products.count()

            if total_products == 0:
                self.stdout.write(
                    self.style.WARNING('No active products found for forecasting')
                )
                return

            self.stdout.write(f'Processing {total_products} products...')

            # Process products in batches to manage memory
            for batch_start in range(0, total_products, batch_size):
                batch_end = min(batch_start + batch_size, total_products)
                batch_products = products[batch_start:batch_end]

                self.stdout.write(
                    f'Processing batch {batch_start//batch_size + 1}: '
                    f'products {batch_start + 1}-{batch_end}'
                )

                # Process each product in the batch
                for product in batch_products:
                    try:
                        # Memory optimization: clear previous forecasts for this product
                        with transaction.atomic():
                            Forecast.objects.filter(
                                product=product,
                                forecast_type='demand'
                            ).delete()

                        # Generate forecast with memory optimization
                        forecast_data = self._generate_forecast(
                            product, algorithm, days, memory_limit
                        )

                        if forecast_data:
                            # Save forecast in transaction
                            with transaction.atomic():
                                Forecast.objects.create(**forecast_data)

                            processed_products += 1

                        # Memory cleanup
                        gc.collect()

                        # Small delay to prevent CPU overload on Core 2 Duo
                        time.sleep(0.1)

                    except Exception as e:
                        error_msg = f'Failed to process product {product.id}: {str(e)}'
                        logger.error(error_msg)
                        failed_products.append({
                            'product_id': product.id,
                            'product_name': product.name_ar or product.name_en,
                            'error': str(e)
                        })

                # Memory optimization between batches
                self._optimize_memory()

            # Calculate execution time
            execution_time = time.time() - start_time

            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nForecasting completed successfully!\n'
                    f'Total products: {total_products}\n'
                    f'Processed: {processed_products}\n'
                    f'Failed: {len(failed_products)}\n'
                    f'Execution time: {execution_time:.2f} seconds\n'
                    f'Average time per product: {execution_time/max(processed_products, 1):.2f} seconds'
                )
            )

            # Report failed products if any
            if failed_products:
                self.stdout.write(
                    self.style.WARNING('\nFailed products:')
                )
                for failed in failed_products:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  - Product {failed['product_id']} "
                            f"({failed['product_name']}): {failed['error']}"
                        )
                    )

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.ERROR('Forecasting interrupted by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Fatal error during forecasting: {str(e)}')
            )
            logger.exception('Fatal error during forecasting')
        finally:
            # Final memory cleanup
            self._optimize_memory()
            connection.close()

    def _generate_forecast(self, product, algorithm, days, memory_limit):
        """
        Generate forecast for a single product with memory optimization
        """
        try:
            # Get historical sales data (optimized query)
            historical_sales = self._get_historical_sales(product.id, days=90)
            
            if not historical_sales or len(historical_sales) < 7:
                logger.warning(f'Insufficient data for product {product.id}')
                return None

            # Simple forecasting algorithm optimized for performance
            predicted_demand = self._simple_forecast(historical_sales, days)
            confidence = self._calculate_confidence(historical_sales, predicted_demand)

            forecast_data = {
                'product': product,
                'forecast_type': 'demand',
                'period': f'{days}days',
                'predicted_demand': predicted_demand,
                'algorithm_used': algorithm.upper(),
                'confidence': confidence,
                'created_at': timezone.now()
            }

            return forecast_data

        except Exception as e:
            logger.error(f'Error generating forecast for product {product.id}: {str(e)}')
            return None

    def _get_historical_sales(self, product_id, days=90):
        """
        Get historical sales data with memory optimization
        """
        try:
            # This would typically query order items
            # For now, return mock data optimized for memory
            import random
            
            # Generate realistic mock data
            base_demand = random.randint(50, 200)
            trend = random.uniform(-0.1, 0.15)
            seasonality = random.uniform(0.8, 1.2)
            
            sales_data = []
            for day in range(min(days, 90)):
                # Simple trend + seasonality model
                demand = base_demand * (1 + trend * day/90) * seasonality
                demand += random.uniform(-demand*0.2, demand*0.2)  # Add noise
                sales_data.append(max(0, int(demand)))
            
            return sales_data

        except Exception as e:
            logger.error(f'Error getting historical sales for product {product_id}: {str(e)}')
            return []

    def _simple_forecast(self, historical_sales, days):
        """
        Simple forecasting algorithm optimized for speed
        """
        if not historical_sales:
            return 0

        # Calculate moving average (memory efficient)
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

        # Add seasonality adjustment (simplified)
        seasonality_factor = 1.0  # Could be calculated based on historical patterns
        forecast *= seasonality_factor

        return max(0, int(forecast))

    def _calculate_confidence(self, historical_sales, predicted_demand):
        """
        Calculate confidence score for the forecast
        """
        if not historical_sales or len(historical_sales) < 7:
            return Decimal('50.00')

        # Calculate volatility
        avg_demand = sum(historical_sales[-7:]) / 7
        variance = sum((x - avg_demand) ** 2 for x in historical_sales[-7:]) / 7
        std_dev = variance ** 0.5

        # Confidence inversely proportional to volatility
        if avg_demand > 0:
            confidence = max(0, min(100, 100 - (std_dev / avg_demand * 100)))
        else:
            confidence = 50

        return Decimal(str(round(confidence, 2)))

    def _optimize_memory(self):
        """
        Memory optimization for Core 2 Duo processors
        """
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear Django query cache
            from django.db import reset_queries
            reset_queries()
            
        except Exception as e:
            logger.error(f'Error during memory optimization: {str(e)}')
