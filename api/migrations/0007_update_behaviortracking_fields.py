"""
Update BehaviorTracking model with new fields for session tracking
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_add_erpnext_sync_log_indexes'),
    ]

    operations = [
        # Make user field nullable to allow anonymous tracking
        migrations.AlterField(
            model_name='behaviortracking',
            name='user',
            field=models.ForeignKey(
                blank=True, 
                db_column='user_id', 
                null=True, 
                on_delete=django.db.models.deletion.CASCADE, 
                to='api.user'
            ),
        ),
        # Add new fields
        migrations.AddField(
            model_name='behaviortracking',
            name='session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='behaviortracking',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='behaviortracking',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        # Add new indexes
        migrations.AddIndex(
            model_name='behaviortracking',
            index=models.Index(fields=['session_id'], name='api_behaviortracking_session_id_idx'),
        ),
    ]
