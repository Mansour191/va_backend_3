from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from core.schema import schema

# إنشاء view مخصص لتجاوز إعدادات MIDDLEWARE
class SafeGraphQLView(GraphQLView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # استخدام الـ view الآمن
    path('api/graphql/', csrf_exempt(SafeGraphQLView.as_view(graphiql=True, schema=schema))),
    path('api/graphql/batch/', csrf_exempt(SafeGraphQLView.as_view(schema=schema, batch=True))),
    
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)