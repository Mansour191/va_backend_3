"""
Dashboard and Settings Models for VynilArt API
"""
from django.db import models


class DashboardSettings(models.Model):
    """
    Dashboard settings model matching api_dashboardsettings table
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        'api.User', 
        on_delete=models.CASCADE,
        related_name='dashboard_settings',
        db_column='user_id'
    )
    widgets = models.JSONField(default=dict, blank=True)
    layout = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_dashboardsettings'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} Dashboard Settings"
