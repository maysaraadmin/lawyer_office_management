from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router for API endpoints
router = DefaultRouter()

# Register app ViewSets
# Note: We'll register ViewSets when they are created

# Include app URLs
urlpatterns = [
    # Authentication endpoints
    path('auth/', include('apps.users.urls')),
    
    # Client endpoints
    path('clients/', include('apps.clients.urls')),
    
    # Appointment endpoints
    path('appointments/', include('apps.appointments.urls')),
    
    # Include the router URLs (for ViewSets)
    path('', include(router.urls)),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
