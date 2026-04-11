"""
API URLs for VynilArt GraphQL Application
This project uses GraphQL only - no REST endpoints needed
"""

from django.urls import path
from graphene_django import GraphQLView
from . import views

app_name = 'api'

urlpatterns = [
    # Main GraphQL Endpoint
    path('graphql/', GraphQLView.as_view(graphiql=True), name='graphql'),
    
    # Health check endpoint (optional)
    path('health/', views.HealthView.as_view(), name='health'),
]
