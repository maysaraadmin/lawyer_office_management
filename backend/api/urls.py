from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router for API endpoints
router = DefaultRouter()

# Include app URLs
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
