"""
Conversation History Models for VynilArt API
"""
from django.db import models


class ConversationHistory(models.Model):
    """
    Conversation history model matching api_conversationhistory table
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)
    message = models.TextField()
    source = models.CharField(max_length=50, default='user')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    related_project = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_conversationhistory'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['role']),
            models.Index(fields=['source']),
            models.Index(fields=['message_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['related_project']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session_id} - {self.role}"
