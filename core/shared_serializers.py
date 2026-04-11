"""
Shared Serializers for VynilArt API
Reusable serializers for cross-domain functionality
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SharedUserSerializer(serializers.ModelSerializer):
    """Shared user serializer for cross-domain use"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class SharedProductSerializer(serializers.Serializer):
    """Shared product reference serializer"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class SharedCategorySerializer(serializers.Serializer):
    """Shared category reference serializer"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()


__all__ = [
    'SharedUserSerializer',
    'SharedProductSerializer',
    'SharedCategorySerializer',
]
