from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Lawyer Office Management API",
      default_version='v1',
      description="API for managing lawyer office operations",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Import health check view
from apps.core.views.health import HealthCheckView

# API URL Configuration
api_patterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # Authentication
    path('auth/', include('apps.users.urls')),  # Authentication endpoints
    
    # App-specific endpoints
    path('appointments/', include('apps.appointments.urls')),  # Appointments endpoints
    path('clients/', include('apps.clients.urls')),  # Clients endpoints
    
    # API Documentation
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    # Root URL redirects to API documentation
    path('', RedirectView.as_view(url='/api/v1/docs/', permanent=False)),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1 (only include once)
    path('api/v1/', include(api_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
