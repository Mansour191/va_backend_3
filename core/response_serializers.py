"""
Response Serializers for VynilArt API
Standard response formats for API endpoints
"""

from rest_framework import serializers


class PaginationSerializer(serializers.Serializer):
    """Standard pagination serializer"""
    count = serializers.IntegerField()
    next = serializers.URLField()
    previous = serializers.URLField()
    total_pages = serializers.IntegerField()
    current_page = serializers.IntegerField()
    page_size = serializers.IntegerField()


class ErrorSerializer(serializers.Serializer):
    """Standard error response serializer"""
    error = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField()
    timestamp = serializers.DateTimeField()


class SuccessSerializer(serializers.Serializer):
    """Standard success response serializer"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()
    timestamp = serializers.DateTimeField()


class BulkOperationSerializer(serializers.Serializer):
    """Bulk operation response serializer"""
    success_count = serializers.IntegerField()
    error_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.DictField())


__all__ = [
    'PaginationSerializer',
    'ErrorSerializer',
    'SuccessSerializer',
    'BulkOperationSerializer',
]
