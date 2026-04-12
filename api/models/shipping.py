"""
Shipping Models for VynilArt API
"""
from django.db import models


class ShippingMethod(models.Model):
    """
    Shipping methods matching api_shipping_method table
    """
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        'api.Organization',
        on_delete=models.CASCADE,
        related_name='shipping_methods',
        db_column='organization_id',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    provider_name = models.CharField(max_length=100, blank=True, null=True)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estimated_days = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_shipping_method'
        indexes = [
            models.Index(fields=['is_active'], name='shipping_active_idx'),
            models.Index(fields=['organization'], name='shipping_org_idx'),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.organization.name_ar}"


class ShippingPrice(models.Model):
    """
    Shipping prices linking wilayas with shipping methods
    """
    wilaya = models.ForeignKey(
        'Shipping', 
        on_delete=models.CASCADE, 
        related_name='shipping_prices'
    )
    shipping_method = models.ForeignKey(
        ShippingMethod, 
        on_delete=models.CASCADE, 
        related_name='prices'
    )
    
    # Pricing for different service types
    home_delivery_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Home Delivery Price'
    )
    stop_desk_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Stop Desk Price'
    )
    express_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Express Price'
    )
    pickup_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Pickup Point Price'
    )
    
    # Additional pricing options
    free_shipping_minimum = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Free Shipping Minimum'
    )
    weight_surcharge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Weight Surcharge (per kg)'
    )
    volume_surcharge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Volume Surcharge (per m³)'
    )
    
    # Service level options
    cod_available = models.BooleanField(default=True, verbose_name='COD Available')
    cod_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='COD Fee'
    )
    insurance_available = models.BooleanField(default=False, verbose_name='Insurance Available')
    insurance_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        help_text="Insurance rate as percentage of declared value"
    )
    tracking_available = models.BooleanField(default=True, verbose_name='Tracking Available')
    
    # Restrictions
    max_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum weight for this price"
    )
    max_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum declared value for this price"
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Validity period
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shipping Price'
        verbose_name_plural = 'Shipping Prices'
        unique_together = ['wilaya', 'shipping_method']
        indexes = [
            models.Index(fields=['wilaya', 'shipping_method']),
            models.Index(fields=['is_active']),
            models.Index(fields=['home_delivery_price']),
            models.Index(fields=['stop_desk_price']),
        ]

    def __str__(self):
        return f"{self.wilaya.name_ar} - {self.shipping_method.name}"


class Shipping(models.Model):
    """
    Shipping model matching api_shipping table
    """
    id = models.AutoField(primary_key=True)
    wilaya_id = models.CharField(max_length=10, unique=True)
    name_ar = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255)
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2, default=400)
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=700)
    is_active = models.BooleanField(default=True)
    regions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_shipping'
        indexes = [
            models.Index(fields=['wilaya_id']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['wilaya_id']

    def __str__(self):
        return f"{self.name_ar} ({self.wilaya_id})"
