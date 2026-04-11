from django.contrib import admin
from django.utils.html import format_html
from api import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'slug', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name_ar', 'name_en', 'slug']
    prepopulated_fields = {'slug': ('name_ar',)}
    readonly_fields = ['created_at', 'updated_at']


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1
    readonly_fields = ['created_at']


class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 1
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'slug', 'category', 'base_price', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_featured', 'is_new', 'on_sale', 'category', 'created_at']
    search_fields = ['name_ar', 'name_en', 'slug', 'description_ar', 'description_en']
    prepopulated_fields = {'slug': ('name_ar',)}
    readonly_fields = ['created_at', 'updated_at', 'last_synced_at']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name_ar', 'name_en', 'slug', 'category', 'description_ar', 'description_en')
        }),
        ('Pricing', {
            'fields': ('base_price', 'cost', 'on_sale', 'discount_percent')
        }),
        ('Inventory', {
            'fields': ('stock', 'weight', 'dimensions')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'tags')
        }),
        ('ERPNext Integration', {
            'fields': ('sync_status', 'erpnext_item_code', 'sync_error', 'last_synced_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'price_per_m2', 'is_premium', 'is_active', 'created_at']
    list_filter = ['is_premium', 'is_active', 'created_at']
    search_fields = ['name_ar', 'name_en', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['wilaya_id', 'name_ar', 'name_fr', 'stop_desk_price', 'home_delivery_price', 'is_active']
    list_filter = ['is_active']
    search_fields = ['wilaya_id', 'name_ar', 'name_fr']
    readonly_fields = ['created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class OrderTimelineInline(admin.TabularInline):
    model = models.OrderTimeline
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'total_amount', 'status', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'phone', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'last_synced_at']
    inlines = [OrderItemInline, OrderTimelineInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'customer_name', 'phone', 'email')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'wilaya')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount_amount', 'total_amount')
        }),
        ('Status', {
            'fields': ('status', 'payment_method', 'payment_status')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('ERPNext Integration', {
            'fields': ('sync_status', 'erpnext_sales_order_id', 'sync_error', 'last_synced_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'method', 'status', 'transaction_id', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'valid_from', 'valid_to']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'material', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name_ar', 'product__name_en']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name_ar', 'product__name_en']
    readonly_fields = ['created_at']


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'is_verified', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['user__username', 'product__name_ar', 'product__name_en', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__product__name_ar', 'user__username', 'reason']
    readonly_fields = ['created_at']


@admin.register(models.DesignCategory)
class DesignCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'slug', 'is_active', 'design_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_ar', 'name_en', 'slug']
    prepopulated_fields = {'slug': ('name_ar',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'user', 'status', 'is_featured', 'likes', 'downloads', 'created_at']
    list_filter = ['status', 'is_featured', 'is_active', 'category', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'generated_at']


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']


@admin.register(models.Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_type', 'priority', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_resolved', 'created_at']
    search_fields = ['product__name_ar', 'product__name_en', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.ERPNextSyncLog)
class ERPNextSyncLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'status', 'records_synced', 'timestamp']
    list_filter = ['action', 'status', 'timestamp']
    search_fields = ['action', 'message', 'error_message']
    readonly_fields = ['timestamp']


@admin.register(models.BehaviorTracking)
class BehaviorTrackingAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target_type', 'target_id', 'created_at']
    list_filter = ['action', 'target_type', 'created_at']
    search_fields = ['user__username', 'action']
    readonly_fields = ['created_at']


@admin.register(models.Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ['product', 'forecast_type', 'period', 'predicted_demand', 'confidence', 'created_at']
    list_filter = ['forecast_type', 'period', 'created_at']
    search_fields = ['product__name_ar', 'product__name_en']
    readonly_fields = ['created_at']


@admin.register(models.CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.PricingEngine)
class PricingEngineAdmin(admin.ModelAdmin):
    list_display = ['raw_material_cost', 'labor_cost', 'international_shipping']
    readonly_fields = []


@admin.register(models.BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'slug', 'created_at', 'updated_at']
    search_fields = ['name_ar', 'name_en', 'slug']
    prepopulated_fields = {'slug': ('name_ar',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title_ar', 'title_en', 'slug', 'category', 'author', 'is_published', 'views', 'created_at']
    list_filter = ['is_published', 'category', 'author', 'created_at']
    search_fields = ['title_ar', 'title_en', 'content_ar', 'content_en']
    prepopulated_fields = {'slug': ('title_ar',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']


@admin.register(models.ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'role', 'source', 'confidence', 'created_at']
    list_filter = ['role', 'source', 'created_at']
    search_fields = ['session_id', 'message']
    readonly_fields = ['created_at']


@admin.register(models.DashboardSettings)
class DashboardSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(models.WishlistSettings)
class WishlistSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_per_page', 'sort_by', 'email_notifications', 'push_notifications', 'created_at']
    list_filter = ['email_notifications', 'push_notifications', 'auto_remove_out_of_stock']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


# Customize admin site
admin.site.site_header = 'VinylArt Administration'
admin.site.site_title = 'VinylArt Admin'
admin.site.index_title = 'Welcome to VinylArt Administration'
