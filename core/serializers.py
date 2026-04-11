"""
Core Serializers Module for VynilArt API
This module provides organized access to all core serializers
"""

# Import all core serializers
from .base_serializers import (
    BaseTimestampedSerializer,
    BaseAuditedSerializer,
)

from .response_serializers import (
    PaginationSerializer,
    ErrorSerializer,
    SuccessSerializer,
    BulkOperationSerializer,
)

from .shared_serializers import (
    SharedUserSerializer,
    SharedProductSerializer,
    SharedCategorySerializer,
)

# Export all serializers
__all__ = [
    # Base serializers
    'BaseTimestampedSerializer',
    'BaseAuditedSerializer',
    
    # Response serializers
    'PaginationSerializer',
    'ErrorSerializer',
    'SuccessSerializer',
    'BulkOperationSerializer',
    
    # Shared serializers
    'SharedUserSerializer',
    'SharedProductSerializer',
    'SharedCategorySerializer',
]
