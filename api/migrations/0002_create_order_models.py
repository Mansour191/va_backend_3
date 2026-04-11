# Generated migration for Order models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_add_product_materials_manytomany'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_number', models.CharField(max_length=50, unique=True, editable=False)),
                ('customer_name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, null=True)),
                ('shipping_address', models.TextField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('payment_method', models.CharField(default='cod', max_length=20)),
                ('payment_status', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, null=True)),
                ('sync_status', models.CharField(default='pending', max_length=20)),
                ('erpnext_sales_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('sync_error', models.TextField(blank=True, null=True)),
                ('last_synced_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='auth.user')),
                ('wilaya', models.ForeignKey(blank=True, db_column='wilaya_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='api.shipping')),
            ],
            options={
                'db_table': 'api_order',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['order_number'], name='api_order_order_number_idx'),
                    models.Index(fields=['user'], name='api_order_user_idx'),
                    models.Index(fields=['status'], name='api_order_status_idx'),
                    models.Index(fields=['created_at'], name='api_order_created_at_idx'),
                    models.Index(fields=['wilaya'], name='api_order_wilaya_idx'),
                    models.Index(fields=['payment_method'], name='api_order_payment_method_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('width', models.DecimalField(decimal_places=2, max_digits=10)),
                ('height', models.DecimalField(decimal_places=2, max_digits=10)),
                ('dimension_unit', models.CharField(default='cm', max_length=10)),
                ('marble_texture', models.CharField(blank=True, max_length=100, null=True)),
                ('custom_design', models.TextField(blank=True, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.ForeignKey(blank=True, db_column='material_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.material')),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.order')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
            options={
                'db_table': 'api_orderitem',
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['order'], name='api_orderitem_order_idx'),
                    models.Index(fields=['product'], name='api_orderitem_product_idx'),
                    models.Index(fields=['material'], name='api_orderitem_material_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OrderTimeline',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=50)),
                ('note', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.CASCADE, related_name='timeline', to='api.order')),
                ('user', models.ForeignKey(blank=True, db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'db_table': 'api_ordertimeline',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['order'], name='api_ordertimeline_order_idx'),
                    models.Index(fields=['status'], name='api_ordertimeline_status_idx'),
                    models.Index(fields=['timestamp'], name='api_ordertimeline_timestamp_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(max_length=50)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('gateway_response', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='api.order')),
            ],
            options={
                'db_table': 'api_payment',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['order'], name='api_payment_order_idx'),
                    models.Index(fields=['status'], name='api_payment_status_idx'),
                    models.Index(fields=['transaction_id'], name='api_payment_transaction_id_idx'),
                    models.Index(fields=['created_at'], name='api_payment_created_at_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(default='percentage', max_length=20)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('max_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('usage_limit', models.IntegerField(blank=True, null=True)),
                ('used_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_coupon',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['code'], name='api_coupon_code_idx'),
                    models.Index(fields=['is_active'], name='api_coupon_is_active_idx'),
                    models.Index(fields=['valid_from'], name='api_coupon_valid_from_idx'),
                    models.Index(fields=['valid_to'], name='api_coupon_valid_to_idx'),
                ],
            },
        ),
    ]
