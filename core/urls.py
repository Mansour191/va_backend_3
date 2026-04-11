"""
GraphQL URL Configuration
"""
from django.urls import path
from django.http import JsonResponse, HttpResponseRedirect

# Simple root view
def home_view(request):
    return JsonResponse({
        'message': 'Welcome to VynilArt API',
        'graphql_endpoint': '/api/graphql/',  # استخدام المسار الجديد
        'graphql_batch_endpoint': '/api/graphql/batch/',
        'admin_panel': '/admin/'
    })

# إعادة توجيه المسار القديم إلى الجديد
def graphql_redirect(request):
    return HttpResponseRedirect('/api/graphql/')

def graphql_batch_redirect(request):
    return HttpResponseRedirect('/api/graphql/batch/')

urlpatterns = [
    path('', home_view, name='home'),
    path('graphql/', graphql_redirect, name='graphql'),
    path('graphql/batch/', graphql_batch_redirect, name='graphql_batch'),
]
