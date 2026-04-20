"""
User Models for VynilArt API
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
import uuid


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    @property
    def get_user_roles(self):
        """
        Get user's group names from auth_group table
        Returns list of group names the user belongs to
        """
        return [group.name for group in self.groups.all()]


class UserProfile(models.Model):
    """
    Extended user profile information matching api_userprofile table
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        'api.User',  # Reference to Django's built-in User model
        on_delete=models.CASCADE,
        related_name='profile',
        db_column='user_id'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_userprofile'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} Profile"


class UserProfileBeforeUpdate(models.Model):
    """
    Audit trail for user profile changes before updates
    """
    id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='audit_trail',
        db_column='user_profile_id'
    )
    
    # Original profile data snapshot
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    
    # New audit fields
    update_reason = models.TextField(blank=True, null=True, help_text="Reason for the profile update")
    updated_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profile_updates',
        db_column='updated_by_id'
    )
    device_info = models.CharField(max_length=500, blank=True, null=True, help_text="Device/browser information")
    change_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of change: profile_update, settings_change, etc.")
    snapshot_date = models.DateTimeField(auto_now_add=True, help_text="When this snapshot was created")
    
    # Original timestamps from the profile being updated
    original_created_at = models.DateTimeField()
    original_updated_at = models.DateTimeField()

    class Meta:
        db_table = 'api_userprofile_before_update'
        indexes = [
            models.Index(fields=['user_profile']),
            models.Index(fields=['snapshot_date']),
            models.Index(fields=['updated_by']),
            models.Index(fields=['change_type']),
        ]
        ordering = ['-snapshot_date']

    def __str__(self):
        return f"Snapshot of {self.user_profile.user.username} Profile - {self.snapshot_date}"
