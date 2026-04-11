"""
Product Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.product import (
    Category, Material, Product, ProductImage, 
    ProductVariant, ProductMaterial
)


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    children_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name_ar', 'name_en', 'slug', 'icon', 'waste_percent',
            'is_active', 'image', 'description', 'parent', 'sort_order',
            'meta_title', 'meta_description', 'created_at', 'updated_at',
            'children_count', 'product_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """Count direct children"""
        return obj.children.filter(is_active=True).count()
    
    def get_product_count(self, obj):
        """Count products in this category"""
        return obj.products.filter(is_active=True).count()


class MaterialSerializer(serializers.ModelSerializer):
    """Material serializer"""
    class Meta:
        model = Material
        fields = [
            'id', 'name_ar', 'name_en', 'slug', 'description',
            'price_per_m2', 'is_premium', 'is_active', 'image',
            'properties', 'durability_years', 'maintenance_notes',
            'supplier', 'supplier_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'image_url', 'alt_text', 'is_main',
            'sort_order', 'title', 'caption', 'file_size',
            'width', 'height', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Product variant serializer"""
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'name', 'sku', 'price', 'compare_at_price',
            'stock', 'attributes', 'option1', 'option2', 'option3',
            'weight', 'dimensions', 'barcode', 'is_active',
            'created_at', 'updated_at', 'is_available'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_available(self, obj):
        """Check if variant is available"""
        return obj.is_active and obj.stock > 0


class ProductMaterialSerializer(serializers.ModelSerializer):
    """Product material assignment serializer"""
    material_name = serializers.CharField(source='material.name_ar', read_only=True)
    
    class Meta:
        model = ProductMaterial
        fields = [
            'id', 'product', 'material', 'is_active', 'price_override',
            'created_at', 'updated_at', 'material_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    category_name = serializers.CharField(source='category.name_ar', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    available_materials = ProductMaterialSerializer(
        source='available_materials', many=True, read_only=True
    )
    current_price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_ar', 'name_en', 'slug', 'description_ar',
            'description_en', 'base_price', 'cost', 'compare_at_price',
            'category', 'category_name', 'tags', 'on_sale',
            'discount_percent', 'is_featured', 'is_new', 'is_active',
            'is_digital', 'stock', 'stock_status', 'reorder_level',
            'reorder_quantity', 'weight', 'dimensions', 'sku',
            'barcode', 'seo_title', 'seo_description', 'seo_keywords',
            'view_count', 'order_count', 'rating_average',
            'rating_count', 'created_at', 'updated_at',
            'images', 'variants', 'available_materials',
            'current_price', 'is_available', 'main_image'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_current_price(self, obj):
        """Calculate current price with discount"""
        if obj.on_sale and obj.discount_percent > 0:
            return obj.base_price * (1 - obj.discount_percent / 100)
        return obj.base_price
    
    def get_is_available(self, obj):
        """Check if product is available"""
        return obj.is_active and obj.stock > 0
    
    def get_main_image(self, obj):
        """Get main product image"""
        main_image = obj.images.filter(is_main=True).first()
        return main_image.image_url if main_image else None


class ProductCreateSerializer(serializers.ModelSerializer):
    """Product creation serializer"""
    class Meta:
        model = Product
        fields = [
            'name_ar', 'name_en', 'slug', 'description_ar',
            'description_en', 'base_price', 'cost', 'compare_at_price',
            'category', 'tags', 'on_sale', 'discount_percent',
            'is_featured', 'is_new', 'is_active', 'is_digital',
            'stock', 'stock_status', 'reorder_level', 'reorder_quantity',
            'weight', 'dimensions', 'sku', 'barcode',
            'seo_title', 'seo_description', 'seo_keywords'
        ]
    
    def create(self, validated_data):
        """Create product"""
        return Product.objects.create(**validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Product update serializer"""
    class Meta:
        model = Product
        fields = [
            'name_ar', 'name_en', 'slug', 'description_ar',
            'description_en', 'base_price', 'cost', 'compare_at_price',
            'category', 'tags', 'on_sale', 'discount_percent',
            'is_featured', 'is_new', 'is_active', 'is_digital',
            'stock', 'stock_status', 'reorder_level', 'reorder_quantity',
            'weight', 'dimensions', 'sku', 'barcode',
            'seo_title', 'seo_description', 'seo_keywords'
        ]
    
    def update(self, instance, validated_data):
        """Update product"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
