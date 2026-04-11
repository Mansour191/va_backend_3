"""
Core Models - Refactored and Cleaned
All models have been moved to api/models/ organized by domain
This file now only contains essential imports and references
"""

# Import all models from api package to maintain compatibility
from api.models import *

# Legacy imports for backward compatibility
User = api.models.User
UserProfile = api.models.UserProfile

# Export all models for easy access
__all__ = [
    # Import all from api.models
    *api.models.__all__,
]
