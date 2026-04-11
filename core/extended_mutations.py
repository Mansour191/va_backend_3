"""
Advanced GraphQL Mutations for all VynilArt operations
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, JSONString, ID
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.utils import timezone
from . import models
from .schema import *
import uuid

User = get_user_model()


# Additional Input Types for Comprehensive Operations
class CategoryInput(graphene.InputObjectType):
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String(required=True)
    description = String()
    icon = String()
    waste_percent = Float()
    image = String()
    parent_id = Int()
    is_active = Boolean()


class MaterialInput(graphene.InputObjectType):
    name_ar = String(required=True)
    name_en = String(required=True)
    description = String()
    price_per_m2 = Float(required=True)
    is_premium = Boolean()
    is_active = Boolean()
    image = String()
    properties = JSONString()


class ProductUpdateInput(graphene.InputObjectType):
    id = ID(required=True)
    name_ar = String()
    name_en = String()
    slug = String()
    description_ar = String()
    description_en = String()
    base_price = Float()
    cost = Float()
    category_id = Int()
    on_sale = Boolean()
    discount_percent = Int()
    is_featured = Boolean()
    is_new = Boolean()
    is_active = Boolean()
    stock = Int()
    weight = Float()
    dimensions = String()
    tags = List(String)


class OrderUpdateInput(graphene.InputObjectType):
    id = ID(required=True)
    status = String()
    notes = String()


class CouponInput(graphene.InputObjectType):
    code = String(required=True)
    discount_type = String(required=True)  # 'percentage' or 'fixed'
    discount_value = Float(required=True)
    min_amount = Float()
    max_discount = Float()
    usage_limit = Int()
    valid_from = String()
    valid_to = String()
    is_active = Boolean()


class DesignInput(graphene.InputObjectType):
    name = String(required=True)
    description = String()
    image = String()
    category_id = Int()
    is_featured = Boolean()
    is_active = Boolean()
    tags = List(String)
    status = String()


class BlogPostInput(graphene.InputObjectType):
    title_ar = String(required=True)
    title_en = String(required=True)
    slug = String(required=True)
    content_ar = String(required=True)
    content_en = String(required=True)
    summary_ar = String()
    summary_en = String()
    category_id = Int()
    featured_image = String()
    tags = List(String)
    is_published = Boolean()


class NotificationInput(graphene.InputObjectType):
    user_id = ID(required=True)
    title = String(required=True)
    message = String(required=True)
    type = String()
    data = JSONString()


# Advanced Mutations

class UpdateCategory(Mutation):
    class Arguments:
        id = ID(required=True)
        input = CategoryInput()

    category = Field(CategoryNode)
    success = Boolean()
    message = String()

    def mutate(self, info, id, input=None):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return UpdateCategory(success=False, message="Staff privileges required")
        
        try:
            category = models.Category.objects.get(id=id)
            
            if input:
                for field, value in input.items():
                    if hasattr(category, field):
                        setattr(category, field, value)
                
                category.save()
            
            return UpdateCategory(category=category, success=True, message="Category updated successfully")
        except models.Category.DoesNotExist:
            return UpdateCategory(success=False, message="Category not found")
        except Exception as e:
            return UpdateCategory(success=False, message=str(e))


class DeleteCategory(Mutation):
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()

    def mutate(self, info, id):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return DeleteCategory(success=False, message="Staff privileges required")
        
        try:
            category = models.Category.objects.get(id=id)
            category.is_active = False
            category.save()
            return DeleteCategory(success=True, message="Category deactivated successfully")
        except models.Category.DoesNotExist:
            return DeleteCategory(success=False, message="Category not found")
        except Exception as e:
            return DeleteCategory(success=False, message=str(e))


class CreateMaterial(Mutation):
    class Arguments:
        input = MaterialInput(required=True)

    material = Field(MaterialNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateMaterial(success=False, message="Staff privileges required")
        
        try:
            material = models.Material.objects.create(
                name_ar=input.name_ar,
                name_en=input.name_en,
                description=input.description,
                price_per_m2=input.price_per_m2,
                is_premium=input.is_premium or False,
                is_active=input.is_active or True,
                image=input.image,
                properties=input.properties or {}
            )
            
            return CreateMaterial(material=material, success=True, message="Material created successfully")
        except Exception as e:
            return CreateMaterial(success=False, message=str(e))


class UpdateProduct(Mutation):
    class Arguments:
        input = ProductUpdateInput(required=True)

    product = Field(ProductNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return UpdateProduct(success=False, message="Staff privileges required")
        
        try:
            product = models.Product.objects.get(id=input.id)
            
            # Update fields
            for field, value in input.items():
                if field == 'id':
                    continue
                if hasattr(product, field):
                    if field == 'category_id' and value:
                        product.category = models.Category.objects.get(id=value)
                    else:
                        setattr(product, field, value)
            
            product.save()
            return UpdateProduct(product=product, success=True, message="Product updated successfully")
        except models.Product.DoesNotExist:
            return UpdateProduct(success=False, message="Product not found")
        except Exception as e:
            return UpdateProduct(success=False, message=str(e))


class DeleteProduct(Mutation):
    class Arguments:
        id = ID(required=True)

    success = Boolean()
    message = String()

    def mutate(self, info, id):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return DeleteProduct(success=False, message="Staff privileges required")
        
        try:
            product = models.Product.objects.get(id=id)
            product.is_active = False
            product.save()
            return DeleteProduct(success=True, message="Product deactivated successfully")
        except models.Product.DoesNotExist:
            return DeleteProduct(success=False, message="Product not found")
        except Exception as e:
            return DeleteProduct(success=False, message=str(e))


class UpdateOrderStatus(Mutation):
    class Arguments:
        input = OrderUpdateInput(required=True)

    order = Field(OrderNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return UpdateOrderStatus(success=False, message="Authentication required")
        
        try:
            order = models.Order.objects.get(id=input.id)
            
            # Check permissions
            if order.user != info.context.user and not info.context.user.is_staff:
                return UpdateOrderStatus(success=False, message="Permission denied")
            
            # Update status
            if input.status:
                order.status = input.status
                
                # Add timeline entry
                models.OrderTimeline.objects.create(
                    order=order,
                    status=input.status,
                    note=input.notes or f"Status updated to {input.status}",
                    user=info.context.user
                )
            
            if input.notes:
                order.notes = input.notes
            
            order.save()
            return UpdateOrderStatus(order=order, success=True, message="Order updated successfully")
        except models.Order.DoesNotExist:
            return UpdateOrderStatus(success=False, message="Order not found")
        except Exception as e:
            return UpdateOrderStatus(success=False, message=str(e))


class CreateCoupon(Mutation):
    class Arguments:
        input = CouponInput(required=True)

    coupon = Field(CouponNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateCoupon(success=False, message="Staff privileges required")
        
        try:
            from datetime import datetime
            
            coupon = models.Coupon.objects.create(
                code=input.code.upper(),
                discount_type=input.discount_type,
                discount_value=input.discount_value,
                min_amount=input.min_amount or 0,
                max_discount=input.max_discount,
                usage_limit=input.usage_limit,
                is_active=input.is_active or True,
                valid_from=datetime.fromisoformat(input.valid_from) if input.valid_from else None,
                valid_to=datetime.fromisoformat(input.valid_to) if input.valid_to else None
            )
            
            return CreateCoupon(coupon=coupon, success=True, message="Coupon created successfully")
        except Exception as e:
            return CreateCoupon(success=False, message=str(e))


class CreateDesign(Mutation):
    class Arguments:
        input = DesignInput(required=True)

    design = Field(DesignNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateDesign(success=False, message="Authentication required")
        
        try:
            category = None
            if input.category_id:
                category = models.DesignCategory.objects.get(id=input.category_id)
            
            design = models.Design.objects.create(
                name=input.name,
                description=input.description,
                image=input.image,
                category=category,
                user=info.context.user,
                is_featured=input.is_featured or False,
                is_active=input.is_active or True,
                tags=input.tags or [],
                status=input.status or 'pending'
            )
            
            return CreateDesign(design=design, success=True, message="Design created successfully")
        except Exception as e:
            return CreateDesign(success=False, message=str(e))


class CreateBlogPost(Mutation):
    class Arguments:
        input = BlogPostInput(required=True)

    blog_post = Field(BlogPostNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateBlogPost(success=False, message="Authentication required")
        
        try:
            category = None
            if input.category_id:
                category = models.BlogCategory.objects.get(id=input.category_id)
            
            blog_post = models.BlogPost.objects.create(
                title_ar=input.title_ar,
                title_en=input.title_en,
                slug=input.slug,
                content_ar=input.content_ar,
                content_en=input.content_en,
                summary_ar=input.summary_ar,
                summary_en=input.summary_en,
                category=category,
                author=info.context.user,
                featured_image=input.featured_image,
                tags=input.tags or [],
                is_published=input.is_published or False,
                published_at=timezone.now() if input.is_published else None
            )
            
            return CreateBlogPost(blog_post=blog_post, success=True, message="Blog post created successfully")
        except Exception as e:
            return CreateBlogPost(success=False, message=str(e))


class SendNotification(Mutation):
    class Arguments:
        input = NotificationInput(required=True)

    notification = Field('NotificationNode')
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return SendNotification(success=False, message="Staff privileges required")
        
        try:
            user = User.objects.get(id=input.user_id)
            
            notification = models.Notification.objects.create(
                user=user,
                title=input.title,
                message=input.message,
                type=input.type or 'info',
                data=input.data or {}
            )
            
            return SendNotification(notification=notification, success=True, message="Notification sent successfully")
        except User.DoesNotExist:
            return SendNotification(success=False, message="User not found")
        except Exception as e:
            return SendNotification(success=False, message=str(e))


class RemoveFromCart(Mutation):
    class Arguments:
        cart_item_id = ID(required=True)

    success = Boolean()
    message = String()

    def mutate(self, info, cart_item_id):
        if not info.context.user.is_authenticated:
            return RemoveFromCart(success=False, message="Authentication required")
        
        try:
            cart_item = models.CartItem.objects.get(id=cart_item_id, user=info.context.user)
            cart_item.delete()
            return RemoveFromCart(success=True, message="Item removed from cart")
        except models.CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Cart item not found")
        except Exception as e:
            return RemoveFromCart(success=False, message=str(e))


class RemoveFromWishlist(Mutation):
    class Arguments:
        product_id = ID(required=True)

    success = Boolean()
    message = String()

    def mutate(self, info, product_id):
        if not info.context.user.is_authenticated:
            return RemoveFromWishlist(success=False, message="Authentication required")
        
        try:
            product = models.Product.objects.get(id=product_id)
            wishlist_item = models.Wishlist.objects.get(user=info.context.user, product=product)
            wishlist_item.delete()
            return RemoveFromWishlist(success=True, message="Item removed from wishlist")
        except (models.Product.DoesNotExist, models.Wishlist.DoesNotExist):
            return RemoveFromWishlist(success=False, message="Item not found in wishlist")
        except Exception as e:
            return RemoveFromWishlist(success=False, message=str(e))


class UpdateReview(Mutation):
    class Arguments:
        review_id = ID(required=True)
        rating = Int()
        comment = String()

    review = Field(ReviewNode)
    success = Boolean()
    message = String()

    def mutate(self, info, review_id, rating=None, comment=None):
        if not info.context.user.is_authenticated:
            return UpdateReview(success=False, message="Authentication required")
        
        try:
            review = models.Review.objects.get(id=review_id, user=info.context.user)
            
            if rating is not None:
                review.rating = rating
            if comment is not None:
                review.comment = comment
            
            review.save()
            return UpdateReview(review=review, success=True, message="Review updated successfully")
        except models.Review.DoesNotExist:
            return UpdateReview(success=False, message="Review not found")
        except Exception as e:
            return UpdateReview(success=False, message=str(e))


class BulkUpdateProducts(Mutation):
    class Arguments:
        product_ids = List(ID, required=True)
        updates = ProductUpdateInput()

    success = Boolean()
    message = String()
    updated_count = Int()

    def mutate(self, info, product_ids, updates):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return BulkUpdateProducts(success=False, message="Staff privileges required")
        
        try:
            updated_count = 0
            products = models.Product.objects.filter(id__in=product_ids)
            
            for product in products:
                for field, value in updates.items():
                    if field == 'id':
                        continue
                    if hasattr(product, field):
                        if field == 'category_id' and value:
                            product.category = models.Category.objects.get(id=value)
                        else:
                            setattr(product, field, value)
                product.save()
                updated_count += 1
            
            return BulkUpdateProducts(
                success=True, 
                message=f"Updated {updated_count} products successfully",
                updated_count=updated_count
            )
        except Exception as e:
            return BulkUpdateProducts(success=False, message=str(e))


# Advanced Query Extensions

class ExtendedQuery(ObjectType):
    # Analytics and Reporting Queries
    sales_summary = Field(JSONString, start_date=String(), end_date=String())
    top_products = List(ProductNode, limit=Int(default_value=10))
    customer_stats = Field(JSONString)
    inventory_report = Field(JSONString)
    
    # Advanced Search
    advanced_search = List(ProductNode, query=String(), filters=JSONString())
    similar_products = List(ProductNode, product_id=ID())
    
    # User Analytics
    user_activity = Field(JSONString, user_id=ID())
    purchase_history = List(OrderNode, user_id=ID(), limit=Int())
    
    def resolve_sales_summary(self, info, start_date=None, end_date=None):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return {}
        
        # Implement sales summary logic here
        return {
            "total_sales": 0,
            "total_orders": 0,
            "average_order_value": 0,
            "top_products": []
        }
    
    def resolve_top_products(self, info, limit=10):
        if not info.context.user.is_authenticated:
            return []
        
        return models.Product.objects.filter(
            is_active=True
        ).order_by('-base_price')[:limit]
    
    def resolve_customer_stats(self, info):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return {}
        
        return {
            "total_customers": User.objects.count(),
            "active_customers": User.objects.filter(is_active=True).count(),
            "new_customers_this_month": 0
        }
    
    def resolve_inventory_report(self, info):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return {}
        
        return {
            "total_products": models.Product.objects.count(),
            "active_products": models.Product.objects.filter(is_active=True).count(),
            "low_stock_products": models.Product.objects.filter(stock__lt=10).count()
        }
    
    def resolve_advanced_search(self, info, query=None, filters=None):
        if not query:
            return models.Product.objects.none()
        
        queryset = models.Product.objects.filter(is_active=True)
        
        # Apply text search
        queryset = queryset.filter(
            models.Q(name_ar__icontains=query) |
            models.Q(name_en__icontains=query) |
            models.Q(description_ar__icontains=query) |
            models.Q(description_en__icontains=query)
        )
        
        # Apply additional filters if provided
        if filters:
            if filters.get('category_id'):
                queryset = queryset.filter(category_id=filters['category_id'])
            if filters.get('min_price'):
                queryset = queryset.filter(base_price__gte=filters['min_price'])
            if filters.get('max_price'):
                queryset = queryset.filter(base_price__lte=filters['max_price'])
        
        return queryset[:20]
    
    def resolve_similar_products(self, info, product_id):
        try:
            product = models.Product.objects.get(id=product_id)
            return models.Product.objects.filter(
                category=product.category,
                is_active=True
            ).exclude(id=product_id)[:5]
        except models.Product.DoesNotExist:
            return []
    
    def resolve_user_activity(self, info, user_id):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return {}
        
        try:
            user = User.objects.get(id=user_id)
            return {
                "total_orders": models.Order.objects.filter(user=user).count(),
                "total_spent": 0,  # Calculate from orders
                "favorite_categories": [],
                "last_login": user.last_login
            }
        except User.DoesNotExist:
            return {}
    
    def resolve_purchase_history(self, info, user_id=None, limit=None):
        if not info.context.user.is_authenticated:
            return []
        
        if user_id and info.context.user.is_staff:
            # Staff can view any user's history
            orders = models.Order.objects.filter(user_id=user_id)
        else:
            # Users can only view their own history
            orders = models.Order.objects.filter(user=info.context.user)
        
        if limit:
            orders = orders[:limit]
        
        return orders


# Extended Mutation Class
class ExtendedMutation(ObjectType):
    # Category operations
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
    
    # Material operations
    create_material = CreateMaterial.Field()
    
    # Product operations
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    bulk_update_products = BulkUpdateProducts.Field()
    
    # Order operations
    update_order_status = UpdateOrderStatus.Field()
    
    # Coupon operations
    create_coupon = CreateCoupon.Field()
    
    # Design operations
    create_design = CreateDesign.Field()
    
    # Blog operations
    create_blog_post = CreateBlogPost.Field()
    
    # Notification operations
    send_notification = SendNotification.Field()
    
    # User interaction operations
    remove_from_cart = RemoveFromCart.Field()
    remove_from_wishlist = RemoveFromWishlist.Field()
    update_review = UpdateReview.Field()
