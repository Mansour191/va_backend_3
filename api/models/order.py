"""
Order Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import datetime
from .product import Product, Material
from .shipping import Shipping, ShippingMethod


class Order(models.Model):
    """
    Order model matching api_order table
    """
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='orders',
        db_column='user_id'
    )
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    shipping_address = models.TextField()
    wilaya = models.ForeignKey(
        Shipping,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='shipping_orders',
        db_column='wilaya_id'
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='shipping_method_orders',
        db_column='shipping_method_id'
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    shipping_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20, default='cod')
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    sync_status = models.CharField(max_length=20, default='pending')
    erpnext_sales_order_id = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    coupon = models.ForeignKey(
        'api.Coupon',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orders',
        db_column='coupon_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_order'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['wilaya']),
            models.Index(fields=['shipping_method']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['coupon']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def calculate_total_amount(self):
        """
        Calculate total amount based on subtotal, shipping, tax, and discount
        """
        # If shipping_method is selected, use its base_cost
        if self.shipping_method and not self.shipping_cost:
            self.shipping_cost = self.shipping_method.base_cost
        
        return (self.subtotal + self.shipping_cost + self.tax - self.discount_amount)

    def clean(self):
        """
        Cross-validation for Order model
        """
        from django.core.exceptions import ValidationError
        
        # Validate total amount calculation
        calculated_total = self.calculate_total_amount()
        if self.total_amount != calculated_total:
            raise ValidationError({
                'total_amount': f'Total amount mismatch. Calculated: {calculated_total}, Provided: {self.total_amount}'
            })
        
        # Validate discount doesn't exceed subtotal
        if self.discount_amount > self.subtotal:
            raise ValidationError({
                'discount_amount': 'Discount amount cannot exceed subtotal'
            })
        
        # Validate shipping cost is reasonable
        if self.shipping_cost and self.shipping_cost > 10000:  # 10,000 DZD max shipping
            raise ValidationError({
                'shipping_cost': 'Shipping cost seems unusually high'
            })
        
        # Validate subtotal matches sum of items
        if hasattr(self, 'items') and self.items.exists():
            items_subtotal = sum(item.price * item.quantity for item in self.items.all())
            if abs(self.subtotal - items_subtotal) > 0.01:  # Allow small rounding differences
                raise ValidationError({
                    'subtotal': f'Subtotal mismatch with items. Calculated: {items_subtotal}, Provided: {self.subtotal}'
                })

    def save(self, *args, **kwargs):
        """
        Override save method to generate automatic order_number
        and calculate shipping cost
        """
        if not self.order_number:
            # Generate order number with format: VA-YYYYMMDD-XXXXX
            today = datetime.now().strftime('%Y%m%d')
            # Get today's order count
            today_count = Order.objects.filter(
                created_at__date=datetime.now().date()
            ).count()
            # Generate unique order number
            self.order_number = f"VA-{today}-{today_count + 1:05d}"
            
            # Ensure uniqueness by checking if order number already exists
            while Order.objects.filter(order_number=self.order_number).exists():
                today_count += 1
                self.order_number = f"VA-{today}-{today_count + 1:05d}"
        
        # Auto-calculate shipping cost if shipping method is set but cost is not
        if self.shipping_method and (self.shipping_cost == 0 or self.shipping_cost is None):
            self.shipping_cost = self.shipping_method.base_cost
        
        # Recalculate total amount
        if hasattr(self, 'subtotal') and self.subtotal is not None:
            self.total_amount = self.calculate_total_amount()
        
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Order items matching api_orderitem table
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        db_column='order_id'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    material = models.ForeignKey(
        Material, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='material_id'
    )
    width = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.1)]
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.1)]
    )
    dimension_unit = models.CharField(max_length=10, default='cm')
    marble_texture = models.CharField(max_length=100, blank=True, null=True)
    custom_design = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_orderitem'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
            models.Index(fields=['material']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name_ar}"


class OrderTimeline(models.Model):
    """
    Order timeline matching api_ordertimeline table
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='timeline',
        db_column='order_id'
    )
    status = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='user_id'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_ordertimeline'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Payment(models.Model):
    """
    Payment model matching api_payment table
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payments',
        db_column='order_id'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_payment'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number}"
