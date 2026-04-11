"""
Notification and Alert Models for VynilArt API
"""
from django.db import models


class Notification(models.Model):
    """
    Notification model matching api_notification table
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, default='info')
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_notification'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
