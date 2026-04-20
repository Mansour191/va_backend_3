"""
Admin configuration for all API models
"""

from .organization_admin import *
from .main_admin_basic import *

# This will register all admin classes when the app is loaded
# Basic registration without field configurations to avoid conflicts
