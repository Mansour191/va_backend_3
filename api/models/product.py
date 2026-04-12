"""
Product Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Product categories matching api_category table
    """
    id = models.AutoField(primary_key=True)
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    icon = models.CharField(max_length=100, blank=True, null=True)
    waste_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='children',
        db_column='parent_id'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_category'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar


class Material(models.Model):
    """
    Materials matching api_material table
    """
    id = models.AutoField(primary_key=True)
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    properties = models.JSONField(default=dict, blank=True)
    
    # Stock management fields
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(
        max_length=20,
        choices=[
            ('kg', 'kilogram'),
            ('m', 'meter'),
            ('piece', 'piece'),
            ('liter', 'liter'),
            ('meter2', 'square meter'),
        ],
        default='kg'
    )
    
    # Self-referencing supplier field
    supplier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='supplied_materials'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_material'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_premium']),
            models.Index(fields=['current_stock']),
            models.Index(fields=['min_stock_level']),
            models.Index(fields=['unit']),
            models.Index(fields=['supplier']),
        ]
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar

    @property
    def is_low_stock(self):
        """Check if material is below minimum stock level"""
        return self.current_stock <= self.min_stock_level

    @property
    def stock_status(self):
        """Get stock status as string"""
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'


class Product(models.Model):
    """
    Product model matching api_product table
    """
    id = models.AutoField(primary_key=True)
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    description_ar = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Categories and classification
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='products',
        db_column='category_id'
    )
    tags = models.JSONField(default=list, blank=True)
    
    # Status and flags
    on_sale = models.BooleanField(default=False)
    discount_percent = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Inventory
    stock = models.IntegerField(default=0)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_level = models.IntegerField(default=0)
    reorder_quantity = models.IntegerField(default=0)
    
    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    
    # SEO
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.JSONField(default=list, blank=True)
    
    # ERP Integration
    sync_status = models.CharField(max_length=20, default='pending')
    erpnext_item_code = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    
    # Many-to-Many relationship with Materials
    materials = models.ManyToManyField(
        Material,
        through='ProductMaterial',
        related_name='products'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_product'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_new']),
            models.Index(fields=['on_sale']),
            models.Index(fields=['stock']),
            models.Index(fields=['stock_quantity']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name_ar

    @property
    def current_price(self):
        """Calculate current price with discount"""
        if self.on_sale and self.discount_percent > 0:
            return float(self.base_price * (1 - self.discount_percent / 100))
        return float(self.base_price)

    @property
    def stock_status(self):
        """Determine stock status"""
        if self.stock_quantity == 0:
            return 'out_of_stock'
        elif self.stock_quantity <= self.reorder_level:
            return 'low_stock'
        else:
            return 'in_stock'

    @property
    def is_available(self):
        """Check if product is available"""
        return self.is_active and self.stock_quantity > 0

    @property
    def discount_amount(self):
        """Calculate discount amount"""
        if self.on_sale and self.discount_percent > 0:
            return float(self.base_price * (self.discount_percent / 100))
        return 0.0

    @property
    def savings_percentage(self):
        """Calculate savings percentage"""
        if self.on_sale and self.discount_percent > 0:
            return float(self.discount_percent)
        return 0.0

    def calculate_final_cost(self):
        """Calculate final cost based on materials"""
        total_material_cost = sum(
            (pm.material.price_per_m2 * pm.quantity_used) 
            for pm in self.product_materials.all()
        )
        self.final_cost = total_material_cost
        self.save()
        return total_material_cost

    def deduct_materials_from_stock(self, quantity_produced=1):
        """Deduct materials from stock when product is manufactured"""
        for pm in self.product_materials.all():
            material = pm.material
            quantity_to_deduct = pm.quantity_used * quantity_produced
            
            if material.current_stock >= quantity_to_deduct:
                material.current_stock -= quantity_to_deduct
                material.save()
            else:
                # Log insufficient stock warning
                print(f"Warning: Insufficient stock for material {material.name_ar}")
                
                # Optional: Create stock alert
                from .alert import Alert
                Alert.objects.create(
                    type='stock_shortage',
                    message=f"Insufficient stock for {material.name_ar}. Required: {quantity_to_deduct}, Available: {material.current_stock}",
                    related_object_id=material.id
                )


class ProductImage(models.Model):
    """
    Product images matching api_productimage table
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images',
        db_column='product_id'
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_productimage'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name_ar} - {self.name}"


class ProductVariant(models.Model):
    """
    Product variants matching api_productvariant table
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants',
        db_column='product_id'
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_productvariant'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name_ar} - {self.name}"


class ProductMaterial(models.Model):
    """
    Product-Material relationship matching api_product_materials table
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='product_materials',
        db_column='product_id'
    )
    material = models.ForeignKey(
        Material, 
        on_delete=models.CASCADE, 
        related_name='product_materials',
        db_column='material_id'
    )
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(
        max_length=20,
        choices=[
            ('kg', 'kilogram'),
            ('m', 'meter'),
            ('piece', 'piece'),
            ('liter', 'liter'),
            ('meter2', 'square meter'),
        ],
        default='kg'
    )
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_product_materials'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['material']),
        ]
        unique_together = ['product', 'material']
        ordering = ['product', 'material']

    def __str__(self):
        return f"{self.product.name_ar} - {self.material.name_ar}"
