"""
Product Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg, Q
from decimal import Decimal
from api.models.product import Category, Material, Product, ProductVariant, ProductMaterial, ProductImage
from api.models.product_image import ProductImageEnhanced


class CategoryType(DjangoObjectType):
    """Product category type"""
    id = graphene.ID(required=True)
    name_ar = String()
    name_en = String()
    slug = String()
    icon = String()
    waste_percent = Float()
    is_active = Boolean()
    image = String()
    description = String()
    
    # Hierarchical fields
    parent = Field(lambda: CategoryType)
    children = List(lambda: CategoryType)
    children_count = Field(Int)
    
    # SEO fields
    meta_title = String()
    meta_description = String()
    
    # Computed fields
    product_count = Field(Int)
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Category
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'parent': ['exact'],
        }

    def resolve_children(self, info):
        """Get direct children categories"""
        return self.children.filter(is_active=True)

    def resolve_children_count(self, info):
        """Count direct children"""
        return self.children.filter(is_active=True).count()

    def resolve_product_count(self, info):
        """Count products in this category"""
        return self.products.filter(is_active=True).count()


class CategoryInput(graphene.InputObjectType):
    """Input for category creation and updates"""
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String()
    icon = String()
    waste_percent = Float()
    is_active = Boolean()
    image = String()
    description = String()
    parent_id = ID()


class UpdateCategory(Mutation):
    """Update an existing category"""
    
    class Arguments:
        id = ID(required=True)
        input = CategoryInput(required=True)

    success = Boolean()
    message = String()
    category = Field(CategoryType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            category = Category.objects.get(id=id)
            
            # Update fields
            for field, value in input.items():
                if field == 'parent_id' and value:
                    from api.models.product import Category
                    category.parent = Category.objects.get(id=value)
                elif hasattr(category, field):
                    setattr(category, field, value)
            
            category.save()
            
            return UpdateCategory(
                success=True,
                message="Category updated successfully",
                category=category
            )
            
        except Category.DoesNotExist:
            return UpdateCategory(
                success=False,
                message="Category not found",
                errors=["Category not found"]
            )
        except Exception as e:
            return UpdateCategory(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class MaterialType(DjangoObjectType):
    """Material type for products"""
    id = graphene.ID(required=True)
    name_ar = String()
    name_en = String()
    slug = String()
    description = String()
    price_per_m2 = Float()
    is_premium = Boolean()
    is_active = Boolean()
    image = String()
    
    # Stock management fields
    current_stock = Float()
    min_stock_level = Float()
    unit = String()
    is_low_stock = Boolean()
    stock_status = String()
    
    # Supplier information
    supplier = Field(lambda: MaterialType)
    
    # Technical specifications
    properties = JSONString()
    durability_years = Int()
    maintenance_notes = String()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Material
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'is_premium': ['exact'],
            'is_low_stock': ['exact'],
            'unit': ['exact'],
        }

    def resolve_is_low_stock(self, info):
        """Check if material is below minimum stock level"""
        return self.current_stock <= self.min_stock_level

    def resolve_stock_status(self, info):
        """Get stock status as string"""
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.current_stock <= self.min_stock_level:
            return 'low_stock'
        else:
            return 'in_stock'


class ProductType(DjangoObjectType):
    """Enhanced product type"""
    id = graphene.ID(required=True)
    name_ar = String()
    name_en = String()
    slug = String()
    description_ar = String()
    description_en = String()
    
    # Pricing
    base_price = Float()
    cost = Float()
    compare_at_price = Float()
    current_price = Float()
    
    # Categories and classification
    category = Field(CategoryType)
    tags = List(String)
    
    # Status and flags
    on_sale = Boolean()
    discount_percent = Int()
    is_featured = Boolean()
    is_new = Boolean()
    is_active = Boolean()
    is_digital = Boolean()
    
    # Inventory
    stock = Int()
    stock_status = String()
    reorder_level = Int()
    reorder_quantity = Int()
    
    # Physical attributes
    weight = Float()
    dimensions = String()
    sku = String()
    barcode = String()
    
    # SEO
    seo_title = String()
    seo_description = String()
    seo_keywords = List(String)
    
    # Analytics
    view_count = Int()
    order_count = Int()
    rating_average = Float()
    rating_count = Int()
    
    # Relations
    images = List(lambda: ProductImageType)
    variants = List(lambda: ProductVariantType)
    available_materials = List(MaterialType)
    product_materials = List(lambda: ProductMaterialType)
    # reviews = List(lambda: ReviewType)  # Commented out - ReviewType not defined in this schema
    
    # Computed fields
    main_image = String()
    is_available = Boolean()
    discount_amount = Float()
    savings_percentage = Float()
    total_material_cost = Float()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'category': ['exact'],
            'is_active': ['exact'],
            'is_featured': ['exact'],
            'is_new': ['exact'],
            'on_sale': ['exact'],
            'stock': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'base_price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        """Optimize queryset with select_related and prefetch_related"""
        return queryset.select_related(
            'category'
        ).prefetch_related(
            'images',
            'variants',
            'product_materials__material'
        ).only(
            'id', 'name_ar', 'name_en', 'slug', 'description_ar', 'description_en',
            'base_price', 'cost', 'compare_at_price', 'on_sale', 'discount_percent',
            'is_featured', 'is_new', 'is_active', 'is_digital', 'stock', 'reorder_level',
            'reorder_quantity', 'weight', 'dimensions', 'sku', 'barcode',
            'seo_title', 'seo_description', 'seo_keywords', 'view_count',
            'order_count', 'rating_average', 'rating_count', 'created_at', 'updated_at',
            'category_id'
        )

    def resolve_current_price(self, info):
        """Calculate current price with discount"""
        if self.on_sale and self.discount_percent > 0:
            return float(self.base_price * (1 - self.discount_percent / 100))
        return float(self.base_price)

    def resolve_stock_status(self, info):
        """Determine stock status"""
        if self.stock == 0:
            return 'out_of_stock'
        elif self.stock <= self.reorder_level:
            return 'low_stock'
        else:
            return 'in_stock'

    def resolve_main_image(self, info):
        """Get main product image"""
        for image in self.images.all():
            if image.is_main:
                return image.image_url
        return None

    def resolve_is_available(self, info):
        """Check if product is available"""
        return self.is_active and self.stock > 0

    def resolve_discount_amount(self, info):
        """Calculate discount amount"""
        if self.on_sale and self.discount_percent > 0:
            return float(self.base_price * (self.discount_percent / 100))
        return 0.0

    def resolve_savings_percentage(self, info):
        """Calculate savings percentage"""
        if self.on_sale and self.discount_percent > 0:
            return float(self.discount_percent)
        return 0.0

    def resolve_total_material_cost(self, info):
        """Calculate total material cost for this product"""
        total_cost = 0
        for pm in self.product_materials.all():
            if pm.is_active:
                # Convert units to base unit for calculation
                base_quantity = self.convert_to_base_unit(pm.quantity_used, pm.unit)
                total_cost += pm.material.price_per_m2 * base_quantity
        return float(total_cost)

    def convert_to_base_unit(self, quantity, unit):
        """Convert quantity to base unit (m2) for cost calculation"""
        conversion_factors = {
            'kg': 1,  # Assume 1kg = 1m2 for simplicity
            'm': 1,   # 1m = 1m2
            'piece': 0.1,  # 1 piece = 0.1m2 (adjust as needed)
            'liter': 1,  # 1 liter = 1m2 (adjust as needed)
            'meter2': 1  # Already in m2
        }
        return quantity * conversion_factors.get(unit, 1)


class ProductImageType(DjangoObjectType):
    """Product image type matching SQL schema"""
    id = graphene.ID(required=True)
    product = Field(ProductType)
    image_url = String()
    alt_text = String()
    is_main = Boolean()
    sort_order = Int()
    
    created_at = DateTime()

    class Meta:
        model = ProductImage
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'is_main': ['exact'],
            'sort_order': ['exact'],
        }

    

class ProductVariantType(DjangoObjectType):
    """Product variant type"""
    id = graphene.ID(required=True)
    product = Field(ProductType)
    name = String()
    sku = String()
    
    # Pricing and inventory
    price = Float()
    compare_at_price = Float()
    stock = Int()
    
    # Variant attributes
    attributes = JSONString()
    option1 = String()
    option2 = String()
    option3 = String()
    
    # Physical properties
    weight = Float()
    dimensions = String()
    barcode = String()
    
    # Status
    is_active = Boolean()
    
    # Computed fields
    is_available = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = ProductVariant
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'sku': ['exact'],
            'is_active': ['exact'],
            'stock': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_available(self, info):
        """Check if variant is available"""
        return self.is_active and self.stock > 0


class ProductMaterialType(DjangoObjectType):
    """Product material assignment type"""
    id = graphene.ID(required=True)
    product = Field(ProductType)
    material = Field(MaterialType)
    quantity_used = Float()
    unit = String()
    is_active = Boolean()
    material_cost = Float()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = ProductMaterial
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'material': ['exact'],
            'is_active': ['exact'],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        """Optimize queryset with select_related"""
        return queryset.select_related(
            'product',
            'material'
        ).only(
            'id', 'product_id', 'material_id', 'quantity_used', 'unit',
            'cost_per_unit', 'is_active', 'created_at', 'updated_at'
        )

    def resolve_material_cost(self, info):
        """Calculate cost for this material assignment"""
        if self.material and self.quantity_used:
            # Convert to base unit for calculation
            base_quantity = self.convert_to_base_unit(self.quantity_used, self.unit)
            return float(self.material.price_per_m2 * base_quantity)
        return 0.0

    def convert_to_base_unit(self, quantity, unit):
        """Convert quantity to base unit (m2) for cost calculation"""
        conversion_factors = {
            'kg': 1,  # Assume 1kg = 1m2 for simplicity
            'm': 1,   # 1m = 1m2
            'piece': 0.1,  # 1 piece = 0.1m2 (adjust as needed)
            'liter': 1,  # 1 liter = 1m2 (adjust as needed)
            'meter2': 1  # Already in m2
        }
        return quantity * conversion_factors.get(unit, 1)


# Input Types
class ProductInput(graphene.InputObjectType):
    """Input for product creation and updates"""
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String()
    description_ar = String()
    description_en = String()
    
    # Pricing
    base_price = Float(required=True)
    cost = Float()
    compare_at_price = Float()
    
    # Categories
    category_id = ID()
    tags = List(String)
    
    # Status
    on_sale = Boolean()
    discount_percent = Int()
    is_featured = Boolean()
    is_new = Boolean()
    is_active = Boolean()
    
    # Inventory
    stock = Int()
    reorder_level = Int()
    reorder_quantity = Int()
    
    # Physical attributes
    weight = Float()
    dimensions = String()
    sku = String()
    barcode = String()
    
    # SEO
    seo_title = String()
    seo_description = String()
    seo_keywords = List(String)


class ProductImageInput(graphene.InputObjectType):
    """Input for product image"""
    product_id = ID(required=True)
    image_url = String(required=True)
    alt_text = String()
    is_main = Boolean()
    sort_order = Int()
    title = String()
    caption = String()


class ProductVariantInput(graphene.InputObjectType):
    """Input for product variant"""
    product_id = ID(required=True)
    name = String(required=True)
    sku = String()
    price = Float(required=True)
    compare_at_price = Float()
    stock = Int()
    attributes = JSONString()
    option1 = String()
    option2 = String()
    option3 = String()
    weight = Float()
    dimensions = String()
    barcode = String()
    is_active = Boolean()


class MaterialInput(graphene.InputObjectType):
    """Input for material creation and updates"""
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String()
    description = String()
    price_per_m2 = Float()
    is_premium = Boolean()
    is_active = Boolean()
    image = String()
    properties = JSONString()
    
    # Stock management
    current_stock = Float()
    min_stock_level = Float()
    unit = String()
    
    # Supplier
    supplier_id = ID()


class UpdateMaterialStock(Mutation):
    """Update material stock when new shipment arrives"""
    
    class Arguments:
        id = ID(required=True)
        new_stock = Float(required=True)
        operation = String()  # 'add', 'set', 'subtract'

    success = Boolean()
    message = String()
    material = Field(MaterialType)
    errors = List(String)

    def mutate(self, info, id, new_stock, operation='add'):
        try:
            material = Material.objects.get(id=id)
            
            if operation == 'add':
                material.current_stock += new_stock
            elif operation == 'set':
                material.current_stock = new_stock
            elif operation == 'subtract':
                material.current_stock = max(0, material.current_stock - new_stock)
            
            material.save()
            
            return UpdateMaterialStock(
                success=True,
                message=f"Material stock updated successfully. New stock: {material.current_stock}",
                material=material
            )
            
        except Material.DoesNotExist:
            return UpdateMaterialStock(
                success=False,
                message="Material not found",
                errors=["Material not found"]
            )
        except Exception as e:
            return UpdateMaterialStock(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class ProductImageInput(graphene.InputObjectType):
    """Input for product image uploads"""
    product_id = ID(required=True)
    alt_text = String()
    is_feature = Boolean()
    sort_order = Int()


class BulkUploadImages(Mutation):
    """Bulk upload multiple images for a product"""
    
    class Arguments:
        product_id = ID(required=True)
        images = List(String, required=True)  # Base64 encoded images
        alt_texts = List(String)  # Optional alt texts
        set_featured = Boolean()  # Set first image as featured

    success = Boolean()
    message = String()
    images = List(ProductImageType)
    errors = List(String)

    def mutate(self, info, product_id, images, alt_texts=None, set_featured=False):
        try:
            from api.models.product import Product
            import base64
            from django.core.files.base import ContentFile
            
            product = Product.objects.get(id=product_id)
            uploaded_images = []
            
            for i, image_data in enumerate(images):
                # Decode base64 image
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Create image file
                image_data = base64.b64decode(imgstr)
                image_file = ContentFile(image_data, f'product_{product_id}_image_{i}.{ext}')
                
                # Create ProductImage instance
                product_image = ProductImage(
                    product=product,
                    image=image_file,
                    alt_text=alt_texts[i] if alt_texts and i < len(alt_texts) else f'{product.name_ar} - Image {i+1}',
                    sort_order=i,
                    is_feature=(i == 0 and set_featured)
                )
                product_image.save()
                uploaded_images.append(product_image)
            
            return BulkUploadImages(
                success=True,
                message=f"Successfully uploaded {len(uploaded_images)} images",
                images=uploaded_images
            )
            
        except Product.DoesNotExist:
            return BulkUploadImages(
                success=False,
                message="Product not found",
                errors=["Product not found"]
            )
        except Exception as e:
            return BulkUploadImages(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class SetFeaturedImage(Mutation):
    """Set an image as featured for a product"""
    
    class Arguments:
        image_id = ID(required=True)

    success = Boolean()
    message = String()
    image = Field(ProductImageType)
    errors = List(String)

    def mutate(self, info, image_id):
        try:
            from api.models.product_image import ProductImage
            
            product_image = ProductImage.objects.get(id=image_id)
            product_image.set_as_featured()
            
            return SetFeaturedImage(
                success=True,
                message="Image set as featured successfully",
                image=product_image
            )
            
        except ProductImage.DoesNotExist:
            return SetFeaturedImage(
                success=False,
                message="Image not found",
                errors=["Image not found"]
            )
        except Exception as e:
            return SetFeaturedImage(
                success=False,
                message=str(e),
                errors=[str(e)]
            )
    """Input for product material assignment"""
    product_id = ID(required=True)
    material_id = ID(required=True)
    quantity_used = Float(required=True)
    unit = String()
    is_active = Boolean()


class AddProductMaterial(Mutation):
    """Add material to product"""
    
    class Arguments:
        product_id = ID(required=True)
        material_id = ID(required=True)

    success = Boolean()
    message = String()
    product_material = Field(ProductMaterialType)
    errors = List(String)

    def mutate(self, info, product_id, material_id):
        try:
            product = Product.objects.get(id=product_id)
            material = Material.objects.get(id=material_id)
            
            product_material = ProductMaterial.objects.create(
                product=product,
                material=material,
                quantity_used=1.0,
                unit='kg',
                is_active=True
            )
            
            # Update product's final cost
            product.calculate_final_cost()
            
            return AddProductMaterial(
                success=True,
                message="Material added to product successfully",
                product_material=product_material
            )
            
        except (Product.DoesNotExist, Material.DoesNotExist) as e:
            return AddProductMaterial(
                success=False,
                message="Product or Material not found",
                errors=[str(e)]
            )
        except Exception as e:
            return AddProductMaterial(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Mutations
class CreateProduct(Mutation):
    """Create a new product"""
    
    class Arguments:
        input = ProductInput(required=True)

    success = Boolean()
    message = String()
    product = Field(ProductType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            # Handle category
            category = None
            if 'category_id' in input:
                from api.models.product import Category
                category = Category.objects.get(id=input['category_id'])
            
            product = Product.objects.create(
                name_ar=input.name_ar,
                name_en=input.name_en,
                slug=input.slug,
                description_ar=input.description_ar,
                description_en=input.description_en,
                base_price=input.base_price,
                cost=input.cost,
                compare_at_price=input.compare_at_price,
                category=category,
                tags=input.tags,
                on_sale=input.on_sale,
                discount_percent=input.discount_percent,
                is_featured=input.is_featured,
                is_new=input.is_new,
                is_active=input.is_active,
                stock=input.stock,
                reorder_level=input.reorder_level,
                reorder_quantity=input.reorder_quantity,
                weight=input.weight,
                dimensions=input.dimensions,
                sku=input.sku,
                barcode=input.barcode,
                seo_title=input.seo_title,
                seo_description=input.seo_description,
                seo_keywords=input.seo_keywords
            )
            
            return CreateProduct(
                success=True,
                message="Product created successfully",
                product=product
            )
            
        except Exception as e:
            return CreateProduct(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateProduct(Mutation):
    """Update an existing product"""
    
    class Arguments:
        id = ID(required=True)
        input = ProductInput(required=True)

    success = Boolean()
    message = String()
    product = Field(ProductType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            product = Product.objects.get(id=id)
            
            # Update fields
            for field, value in input.items():
                if field == 'category_id' and value:
                    from api.models.product import Category
                    product.category = Category.objects.get(id=value)
                elif hasattr(product, field):
                    setattr(product, field, value)
            
            product.save()
            
            return UpdateProduct(
                success=True,
                message="Product updated successfully",
                product=product
            )
            
        except Product.DoesNotExist:
            return UpdateProduct(
                success=False,
                message="Product not found",
                errors=["Product not found"]
            )
        except Exception as e:
            return UpdateProduct(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class DeleteProduct(Mutation):
    """Delete a product"""
    
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()
    errors = List(String)

    def mutate(self, info, id):
        try:
            product = Product.objects.get(id=id)
            product.delete()
            
            return DeleteProduct(
                success=True,
                message="Product deleted successfully"
            )
            
        except Product.DoesNotExist:
            return DeleteProduct(
                success=False,
                message="Product not found",
                errors=["Product not found"]
            )
        except Exception as e:
            return DeleteProduct(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class ProductQuery(ObjectType):
    """Product queries"""
    
    products = List(ProductType)
    product = Field(ProductType, id=ID(required=True))
    products_connection = DjangoFilterConnectionField(ProductType)
    featured_products = List(ProductType)
    new_products = List(ProductType)
    sale_products = List(ProductType)
    related_products = List(ProductType, product_id=ID(required=True))
    
    def resolve_products(self, info):
        """Get all active products"""
        return Product.objects.filter(is_active=True)
    
    def resolve_product(self, info, id):
        """Get product by ID"""
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_featured_products(self, info):
        """Get featured products"""
        return Product.objects.filter(is_active=True, is_featured=True)
    
    def resolve_new_products(self, info):
        """Get new products"""
        return Product.objects.filter(is_active=True, is_new=True)
    
    def resolve_sale_products(self, info):
        """Get products on sale"""
        return Product.objects.filter(is_active=True, on_sale=True)
    
    def resolve_related_products(self, info, product_id):
        """Get related products based on category"""
        try:
            product = Product.objects.get(id=product_id)
            if product.category:
                return Product.objects.filter(
                    category=product.category,
                    is_active=True
                ).exclude(id=product.id)[:8]
            return []
        except Product.DoesNotExist:
            return []


# Mutation Class
class ProductMutation(ObjectType):
    """Product mutations"""
    
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    update_category = UpdateCategory.Field()
    update_material_stock = UpdateMaterialStock.Field()
    add_product_material = AddProductMaterial.Field()
    bulk_upload_images = BulkUploadImages.Field()
    set_featured_image = SetFeaturedImage.Field()


# Node Classes from core/schema.py
class CategoryNode(DjangoObjectType):
    """Relay Node for Category"""
    class Meta:
        model = Category
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'parent': ['exact'],
        }
    
    # Add custom resolvers for tree structure
    children = List(lambda: CategoryNode)
    level = Int()
    
    def resolve_children(self, info):
        """Get direct children of this category"""
        return Category.objects.filter(parent=self, is_active=True)
    
    def resolve_level(self, info):
        """Calculate level of this category in tree"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level


class MaterialNode(DjangoObjectType):
    """Material node with enhanced filtering"""
    class Meta:
        model = Material
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_premium': ['exact'],
        }


class ProductNode(DjangoObjectType):
    """Enhanced product node with relationships"""
    images = List(lambda: ProductImageNode)
    variants = List(lambda: ProductVariantNode)
    available_materials = List(lambda: ProductMaterialNode)
    category = Field(lambda: CategoryNode)
    
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'is_featured': ['exact'],
            'is_new': ['exact'],
            'on_sale': ['exact'],
            'category': ['exact'],
            'base_price': ['lt', 'lte', 'gt', 'gte'],
        }


class ProductImageNode(DjangoObjectType):
    """Product image node"""
    class Meta:
        model = ProductImage
        interfaces = (relay.Node,)
        fields = '__all__'


class ProductVariantNode(DjangoObjectType):
    """Product variant node"""
    class Meta:
        model = ProductVariant
        interfaces = (relay.Node,)
        fields = '__all__'


class ProductMaterialNode(DjangoObjectType):
    """Product material relationship node"""
    material = Field(lambda: MaterialNode)
    
    class Meta:
        model = ProductMaterial
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'material': ['exact'],
            'is_active': ['exact'],
        }
