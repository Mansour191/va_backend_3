"""
ERPNext Integration Models for VynilArt API
"""
from django.db import models


class ERPNextSyncLog(models.Model):
    """
    ERPNext sync log model matching api_erpnextsynclog table
    """
    id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='running')
    message = models.TextField(blank=True, null=True)
    records_synced = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_erpnextsynclog'
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.status}"
