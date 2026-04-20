"""
AI and Analytics Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .product import Product


class BehaviorTracking(models.Model):
    """
    Behavior tracking model matching api_behaviortracking table
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        db_column='user_id',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    duration = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_behaviortracking'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
            models.Index(fields=['action']),
            models.Index(fields=['target_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.action}"
        return f"Anonymous - {self.action}"


class Forecast(models.Model):
    """
    Forecast model matching api_forecast table
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    forecast_type = models.CharField(max_length=50)
    period = models.CharField(max_length=20)
    predicted_demand = models.IntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    actual_demand = models.IntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    error_margin = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    algorithm_used = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_forecast'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['forecast_type']),
            models.Index(fields=['period']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name_ar} - {self.forecast_type} ({self.period})"


class CustomerSegment(models.Model):
    """
    Customer segment model matching api_customersegment table
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('archived', 'Archived'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    criteria = models.JSONField(default=dict, blank=True)
    criteria_rules = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_sync_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_customersegment'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
            models.Index(fields=['last_sync_date']),
        ]
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name


class CustomerSegmentUser(models.Model):
    """
    Customer segment user relationship matching api_customersegment_users table
    """
    id = models.AutoField(primary_key=True)
    customersegment = models.ForeignKey(
        CustomerSegment, 
        on_delete=models.CASCADE,
        db_column='customersegment_id'
    )
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    added_by_ai = models.BooleanField(default=False)
    engagement_score = models.IntegerField(default=0)

    class Meta:
        db_table = 'api_customersegment_users'
        indexes = [
            models.Index(fields=['customersegment']),
            models.Index(fields=['user']),
            models.Index(fields=['joined_at']),
            models.Index(fields=['added_by_ai']),
            models.Index(fields=['engagement_score']),
        ]
        unique_together = ['customersegment', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.customersegment.name}"


class PricingEngine(models.Model):
    """
    Pricing engine model matching api_pricingengine table
    """
    id = models.AutoField(primary_key=True)
    raw_material_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=500,
        validators=[MinValueValidator(0)]
    )
    labor_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=300,
        validators=[MinValueValidator(0)]
    )
    international_shipping = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=200,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default='DZD')
    tax_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'api_pricingengine'

    def __str__(self):
        return f"Pricing Engine - ID: {self.id}"

    def calculate_total_cost(self):
        """Calculate total cost including tax"""
        base_cost = self.raw_material_cost + self.labor_cost + self.international_shipping
        if self.tax_percentage:
            tax_amount = base_cost * (self.tax_percentage / 100)
            return base_cost + tax_amount
        return base_cost
