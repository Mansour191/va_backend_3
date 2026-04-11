"""
Add forecast enhancement fields: actual_demand, error_margin, algorithm_used
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_update_behaviortracking_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecast',
            name='actual_demand',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='forecast',
            name='error_margin',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='forecast',
            name='algorithm_used',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
