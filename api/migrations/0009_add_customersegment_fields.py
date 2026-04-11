# Generated migration for CustomerSegment fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_add_forecast_enhancement_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='customersegment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customersegment',
            name='priority',
            field=models.IntegerField(default=0),
        ),
        migrations.AddIndex(
            model_name='customersegment',
            index=models.Index(fields=['is_active'], name='api_customersegment_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='customersegment',
            index=models.Index(fields=['priority'], name='api_customersegment_priority_idx'),
        ),
    ]
