"""
Add performance indexes for ERPNext Sync Log table
Optimized for 4GB RAM constraint
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_add_coupon_to_orders'),
    ]

    operations = [
        # Add composite indexes for common query patterns
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_erpnextsynclog_status_timestamp ON api_erpnextsynclog(status, timestamp DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_erpnextsynclog_status_timestamp;"
        ),
        
        # Add index for action filtering
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_erpnextsynclog_action_timestamp ON api_erpnextsynclog(action, timestamp DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_erpnextsynclog_action_timestamp;"
        ),
        
        # Add index for recent logs (most common query)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_erpnextsynclog_timestamp_desc ON api_erpnextsynclog(timestamp DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_erpnextsynclog_timestamp_desc;"
        ),
        
        # Add index for error message filtering (for admin dashboard)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_erpnextsynclog_failed_timestamp ON api_erpnextsynclog(status, timestamp DESC) WHERE status = 'failed';",
            reverse_sql="DROP INDEX IF EXISTS idx_erpnextsynclog_failed_timestamp;"
        ),
    ]
