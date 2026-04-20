"""
System and Integration Models for VynilArt API
"""
from django.db import models
from django.utils import timezone
import json






class SystemConfiguration(models.Model):
    """
    System-wide configuration settings
    """
    CONFIG_TYPES = [
        ('general', 'General'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('security', 'Security'),
        ('backup', 'Backup'),
        ('api', 'API'),
        ('ai', 'AI Services'),
    ]
    
    key = models.CharField(max_length=255)
    value = models.TextField()
    config_type = models.CharField(max_length=50, choices=CONFIG_TYPES)
    
    # Validation and constraints
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
            ('email', 'Email'),
            ('url', 'URL'),
        ],
        default='string'
    )
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, null=True)
    
    # Validation rules
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)
    allowed_values = models.JSONField(default=list, blank=True)
    validation_regex = models.CharField(max_length=500, blank=True, null=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    requires_restart = models.BooleanField(default=False)
    
    # Organization and environment
    organization = models.ForeignKey(
        'api.Organization',
        on_delete=models.CASCADE,
        related_name='configurations'
    )
    environment = models.CharField(
        max_length=20,
        choices=[
            ('development', 'Development'),
            ('staging', 'Staging'),
            ('production', 'Production'),
        ],
        default='production'
    )
    
    # Audit trail
    created_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_configs'
    )
    updated_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='updated_configs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['config_type']),
            models.Index(fields=['organization']),
            models.Index(fields=['environment']),
            models.Index(fields=['is_public']),
        ]
        unique_together = ['key', 'organization', 'environment']

    def __str__(self):
        return f"{self.key} - {self.organization.name}"

    def validate_value(self, value):
        """Validate a value against configuration rules"""
        # Type validation
        if self.data_type == 'integer':
            try:
                value = int(value)
            except ValueError:
                return False, "Must be an integer"
        elif self.data_type == 'float':
            try:
                value = float(value)
            except ValueError:
                return False, "Must be a number"
        elif self.data_type == 'boolean':
            if isinstance(value, str):
                return value.lower() in ['true', 'false', '1', '0']
            return isinstance(value, bool)
        elif self.data_type == 'json':
            try:
                json.loads(value)
            except json.JSONDecodeError:
                return False, "Must be valid JSON"
        
        # Range validation
        if self.min_value is not None and float(value) < self.min_value:
            return False, f"Must be at least {self.min_value}"
        
        if self.max_value is not None and float(value) > self.max_value:
            return False, f"Must be at most {self.max_value}"
        
        # Allowed values validation
        if self.allowed_values and value not in self.allowed_values:
            return False, f"Must be one of: {', '.join(map(str, self.allowed_values))}"
        
        return True, "Valid"

    def get_typed_value(self):
        """Get value in the correct data type"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.data_type == 'json':
            return json.loads(self.value)
        else:
            return self.value


