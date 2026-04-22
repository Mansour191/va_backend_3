"""
API URLs for VynilArt GraphQL Application
This project uses GraphQL only - no REST endpoints needed
GraphQL endpoints are handled in main project URLs.
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health check endpoint only
    path('health/', views.HealthView.as_view(), name='health'),
]
