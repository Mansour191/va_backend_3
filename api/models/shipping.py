"""
Shipping Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    base_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
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
        verbose_name='Home Delivery Price',
        validators=[MinValueValidator(0)]
    )
    stop_desk_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Stop Desk Price',
        validators=[MinValueValidator(0)]
    )
    express_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Express Price',
        validators=[MinValueValidator(0)]
    )
    pickup_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Pickup Point Price',
        validators=[MinValueValidator(0)]
    )
    
    # Additional pricing options
    free_shipping_minimum = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Free Shipping Minimum',
        validators=[MinValueValidator(0)]
    )
    weight_surcharge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Weight Surcharge (per kg)',
        validators=[MinValueValidator(0)]
    )
    volume_surcharge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Volume Surcharge (per m³)',
        validators=[MinValueValidator(0)]
    )
    
    # Service level options
    cod_available = models.BooleanField(default=True, verbose_name='COD Available')
    cod_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='COD Fee',
        validators=[MinValueValidator(0)]
    )
    insurance_available = models.BooleanField(default=False, verbose_name='Insurance Available')
    insurance_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        help_text="Insurance rate as percentage of declared value",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    tracking_available = models.BooleanField(default=True, verbose_name='Tracking Available')
    
    # Restrictions
    max_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum weight for this price",
        validators=[MinValueValidator(0)]
    )
    max_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum declared value for this price",
        validators=[MinValueValidator(0)]
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
    stop_desk_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=400,
        validators=[MinValueValidator(0)]
    )
    home_delivery_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=700,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    regions = models.JSONField(default=list, blank=True)
    
    # Google Maps Integration fields
    pickup_latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        help_text="Pickup point latitude",
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    pickup_longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        help_text="Pickup point longitude",
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    radius_km = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Service radius in kilometers",
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    maps_url = models.URLField(max_length=500, null=True, blank=True, help_text="Google Maps URL for pickup location")
    
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

    def clean(self):
        """
        Cross-validation for Shipping model
        """
        from django.core.exceptions import ValidationError
        
        # Validate coordinate pairs
        if self.pickup_latitude and self.pickup_longitude:
            # Algeria coordinate bounds validation
            if not (19 <= float(self.pickup_latitude) <= 37):
                raise ValidationError({
                    'pickup_latitude': 'Latitude must be within Algeria bounds (19° to 37°)'
                })
            
            if not (-9 <= float(self.pickup_longitude) <= 12):
                raise ValidationError({
                    'pickup_longitude': 'Longitude must be within Algeria bounds (-9° to 12°)'
                })
            
            # Validate radius is reasonable for coordinates
            if self.radius_km and self.radius_km > 500:
                raise ValidationError({
                    'radius_km': 'Service radius too large for pickup location (max 500km)'
                })
        
        # Validate pricing logic
        if self.home_delivery_price <= self.stop_desk_price:
            raise ValidationError({
                'home_delivery_price': 'Home delivery price should be higher than stop desk price'
            })
        
        # Validate prices are reasonable for Algeria market
        if self.home_delivery_price > 5000:  # 5000 DZD max
            raise ValidationError({
                'home_delivery_price': 'Home delivery price seems unusually high for Algeria market'
            })
        
        if self.stop_desk_price > 3000:  # 3000 DZD max
            raise ValidationError({
                'stop_desk_price': 'Stop desk price seems unusually high for Algeria market'
            })
