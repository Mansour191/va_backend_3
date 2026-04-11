"""
Add coupon foreign key to orders table
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_add_orderitem_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                db_column='coupon_id',
                to='api.coupon'
            ),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['coupon'], name='api_order_coupon_idx'),
        ),
    ]
