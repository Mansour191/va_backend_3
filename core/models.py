"""
Core Models Aggregation - Central import point for all API models
This file serves as the main models import point for the application.
All actual model definitions are organized in the api/models/ directory.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
import uuid

# Import all models from api package to maintain compatibility
from api import models as api_models


# Export all models for easy access
__all__ = [
    # Import all from api.models
    *api_models.__all__,
]
