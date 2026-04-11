"""
Base Serializers for VynilArt API
Abstract base classes for all serializers
"""

from rest_framework import serializers


class BaseTimestampedSerializer(serializers.ModelSerializer):
    """Base serializer with timestamp fields"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True


class BaseAuditedSerializer(BaseTimestampedSerializer):
    """Base serializer with audit fields"""
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        abstract = True


__all__ = [
    'BaseTimestampedSerializer',
    'BaseAuditedSerializer',
]
