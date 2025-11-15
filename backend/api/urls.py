from django.urls import path, include

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('apps.users.urls')),
    
    # Dashboard endpoints
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Client endpoints
    path('clients/', include('apps.clients.urls')),
    
    # Appointment endpoints
    path('appointments/', include('apps.appointments.urls')),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
