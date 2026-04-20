# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApiAlert(models.Model):
    id = models.BigAutoField(primary_key=True)
    alert_type = models.CharField(max_length=20)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_resolved = models.BooleanField()
    priority = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    message = models.TextField()
    metadata = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    resolved_at = models.DateTimeField(blank=True, null=True)
    auto_notify = models.BooleanField()
    notification_sent = models.BooleanField()
    notification_sent_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey('ApiProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_alert'


class ApiAlertrule(models.Model):
    id = models.BigAutoField(primary_key=True)
    alert_type = models.CharField(max_length=20)
    is_active = models.BooleanField()
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    notify_admins = models.BooleanField()
    notify_customers = models.BooleanField()
    auto_resolve = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    product = models.ForeignKey('ApiProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_alertrule'
        unique_together = (('product', 'alert_type'),)


class ApiBehaviortracking(models.Model):
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    metadata = models.JSONField()
    created_at = models.DateTimeField()
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_behaviortracking'


class ApiBlogcategory(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_blogcategory'


class ApiBlogpost(models.Model):
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    content_ar = models.TextField()
    content_en = models.TextField()
    summary_ar = models.TextField(blank=True, null=True)
    summary_en = models.TextField(blank=True, null=True)
    featured_image = models.CharField(max_length=500, blank=True, null=True)
    tags = models.JSONField()
    views = models.IntegerField()
    is_published = models.BooleanField()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    author = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(ApiBlogcategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_blogpost'


class ApiCartitem(models.Model):
    quantity = models.IntegerField()
    options = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)
    material = models.ForeignKey('ApiMaterial', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey('ApiProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_cartitem'


class ApiCategory(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    icon = models.CharField(max_length=100, blank=True, null=True)
    waste_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField()
    image = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_category'


class ApiConversationhistory(models.Model):
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)
    message = models.TextField()
    source = models.CharField(max_length=50)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    metadata = models.JSONField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_conversationhistory'


class ApiCoupon(models.Model):
    code = models.CharField(unique=True, max_length=50)
    discount_type = models.CharField(max_length=20)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    usage_limit = models.IntegerField(blank=True, null=True)
    used_count = models.IntegerField()
    is_active = models.BooleanField()
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_coupon'


class ApiCouponcampaign(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField()
    target_audience = models.JSONField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    coupons_count = models.IntegerField()
    total_usage = models.IntegerField()
    total_discount_given = models.DecimalField(max_digits=12, decimal_places=2)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_couponcampaign'


class ApiCouponusage(models.Model):
    id = models.BigAutoField(primary_key=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_amount_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    used_at = models.DateTimeField()
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)
    order = models.ForeignKey('ApiOrder', models.DO_NOTHING)
    coupon = models.ForeignKey('ApiPromotioncoupon', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_couponusage'
        unique_together = (('coupon', 'user', 'order'),)


class ApiCustomersegment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    criteria = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_customersegment'


class ApiCustomersegmentUsers(models.Model):
    customersegment = models.ForeignKey(ApiCustomersegment, models.DO_NOTHING)
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_customersegment_users'
        unique_together = (('customersegment', 'user'),)


class ApiDashboardsettings(models.Model):
    widgets = models.JSONField()
    layout = models.JSONField()
    preferences = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField('ApiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_dashboardsettings'


class ApiDesign(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField()
    is_active = models.BooleanField()
    likes = models.IntegerField()
    downloads = models.IntegerField()
    tags = models.JSONField()
    status = models.CharField(max_length=20)
    generated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey('ApiDesigncategory', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_design'


class ApiDesigncategory(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField()
    design_count = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_designcategory'


class ApiErpnextsynclog(models.Model):
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    message = models.TextField(blank=True, null=True)
    records_synced = models.IntegerField()
    error_message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_erpnextsynclog'


class ApiForecast(models.Model):
    forecast_type = models.CharField(max_length=50)
    period = models.CharField(max_length=20)
    predicted_demand = models.IntegerField(blank=True, null=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField()
    product = models.ForeignKey('ApiProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_forecast'


class ApiMaterial(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2)
    is_premium = models.BooleanField()
    is_active = models.BooleanField()
    image = models.CharField(max_length=500, blank=True, null=True)
    properties = models.JSONField()
    current_stock = models.DecimalField(max_digits=10, decimal_places=2)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    supplier = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_material'


class ApiNotification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50)
    is_read = models.BooleanField()
    data = models.JSONField()
    created_at = models.DateTimeField()
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_notification'


class ApiOrder(models.Model):
    order_number = models.CharField(unique=True, max_length=50)
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=254, blank=True, null=True)
    shipping_address = models.TextField()
    wilaya_id = models.CharField(max_length=10, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)
    payment_status = models.BooleanField()
    notes = models.TextField(blank=True, null=True)
    sync_status = models.CharField(max_length=20)
    erpnext_sales_order_id = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_order'


class ApiOrderitem(models.Model):
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    dimension_unit = models.CharField(max_length=10)
    marble_texture = models.CharField(max_length=100, blank=True, null=True)
    custom_design = models.TextField(blank=True, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    material = models.ForeignKey(ApiMaterial, models.DO_NOTHING, blank=True, null=True)
    order = models.ForeignKey(ApiOrder, models.DO_NOTHING)
    product = models.ForeignKey('ApiProduct', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_orderitem'


class ApiOrdertimeline(models.Model):
    status = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()
    order = models.ForeignKey(ApiOrder, models.DO_NOTHING)
    user = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_ordertimeline'


class ApiPayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    order = models.ForeignKey(ApiOrder, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_payment'


class ApiPricingengine(models.Model):
    raw_material_cost = models.DecimalField(max_digits=10, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    international_shipping = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'api_pricingengine'


class ApiProduct(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    description_ar = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.JSONField()
    on_sale = models.BooleanField()
    discount_percent = models.IntegerField()
    is_featured = models.BooleanField()
    is_new = models.BooleanField()
    is_active = models.BooleanField()
    stock = models.IntegerField()
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField()
    reorder_quantity = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    sku = models.CharField(unique=True, max_length=100)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.JSONField()
    sync_status = models.CharField(max_length=20)
    erpnext_item_code = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    category = models.ForeignKey(ApiCategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_product'


class ApiProductMaterials(models.Model):
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    material = models.ForeignKey(ApiMaterial, models.DO_NOTHING)
    product = models.ForeignKey(ApiProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_product_materials'
        unique_together = (('product', 'material'),)


class ApiProductimage(models.Model):
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=100)
    tags = models.JSONField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    product = models.ForeignKey(ApiProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_productimage'


class ApiProductvariant(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(unique=True, max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    attributes = models.JSONField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    product = models.ForeignKey(ApiProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_productvariant'


class ApiPromotioncoupon(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=20)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    usage_limit = models.IntegerField(blank=True, null=True)
    usage_limit_per_user = models.IntegerField(blank=True, null=True)
    used_count = models.IntegerField()
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    applicable_products = models.JSONField()
    excluded_products = models.JSONField()
    applicable_categories = models.JSONField()
    excluded_categories = models.JSONField()
    applicable_wilayas = models.JSONField()
    applicable_user_segments = models.JSONField()
    first_time_customers_only = models.BooleanField()
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    auto_apply = models.BooleanField()
    stackable = models.BooleanField()
    buy_quantity = models.IntegerField(blank=True, null=True)
    get_quantity = models.IntegerField(blank=True, null=True)
    get_product_id = models.IntegerField(blank=True, null=True)
    tiers = models.JSONField()
    times_used = models.IntegerField()
    total_discount_given = models.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    campaign = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey('ApiUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_promotioncoupon'


class ApiReview(models.Model):
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField()
    helpful_count = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    product = models.ForeignKey(ApiProduct, models.DO_NOTHING)
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_review'
        unique_together = (('user', 'product'),)


class ApiReviewreport(models.Model):
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    review = models.ForeignKey(ApiReview, models.DO_NOTHING)
    user = models.ForeignKey('ApiUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_reviewreport'
        unique_together = (('review', 'user'),)


class ApiShipping(models.Model):
    wilaya_id = models.CharField(unique=True, max_length=10)
    name_ar = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255)
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2)
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField()
    regions = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_shipping'


class ApiShippingmethod(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=20)
    service_type = models.CharField(max_length=20)
    expected_delivery_time = models.IntegerField()
    delivery_days = models.JSONField()
    cutoff_time = models.TimeField(blank=True, null=True)
    logo = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.CharField(max_length=254, blank=True, null=True)
    is_active = models.BooleanField()
    tracking_available = models.BooleanField()
    insurance_available = models.BooleanField()
    cod_available = models.BooleanField()
    coverage_wilayas = models.JSONField()
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_dimensions = models.JSONField()
    tracking_url_template = models.CharField(max_length=200)
    api_endpoint = models.CharField(max_length=200)
    api_key = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_shippingmethod'


class ApiShippingprice(models.Model):
    id = models.BigAutoField(primary_key=True)
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2)
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2)
    express_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pickup_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    free_shipping_minimum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight_surcharge = models.DecimalField(max_digits=10, decimal_places=2)
    volume_surcharge = models.DecimalField(max_digits=10, decimal_places=2)
    cod_available = models.BooleanField()
    cod_fee = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_available = models.BooleanField()
    insurance_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tracking_available = models.BooleanField()
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField()
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    shipping_method = models.ForeignKey(ApiShippingmethod, models.DO_NOTHING)
    wilaya = models.ForeignKey(ApiShipping, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_shippingprice'
        unique_together = (('wilaya', 'shipping_method'),)


class ApiUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    email = models.CharField(unique=True, max_length=254)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField()
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_user'


class ApiUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(ApiUser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_user_groups'
        unique_together = (('user', 'group'),)


class ApiUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(ApiUser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ApiUserprofile(models.Model):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField()
    settings = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField(ApiUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_userprofile'


class ApiWishlist(models.Model):
    created_at = models.DateTimeField()
    product = models.ForeignKey(ApiProduct, models.DO_NOTHING)
    user = models.ForeignKey(ApiUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_wishlist'
        unique_together = (('user', 'product'),)


class ApiWishlistsettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    items_per_page = models.IntegerField()
    sort_by = models.CharField(max_length=20)
    sort_order = models.CharField(max_length=4)
    email_notifications = models.BooleanField()
    push_notifications = models.BooleanField()
    auto_remove_out_of_stock = models.BooleanField()
    auto_remove_discontinued = models.BooleanField()
    make_public = models.BooleanField()
    share_token = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField(ApiUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'api_wishlistsettings'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(ApiUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
