from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Root web URL redirects to dashboard
    path('', RedirectView.as_view(url='/web/dashboard/', permanent=False)),
    
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Main application URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointments, name='appointments'),
    path('clients/', views.clients, name='clients'),
    path('profile/', views.profile, name='profile'),
    
    # API-like URLs for updates
    path('appointments/<int:appointment_id>/<str:status>/', 
         views.update_appointment_status, name='update_appointment_status'),
    path('clients/<int:client_id>/<str:is_active>/', 
         views.toggle_client_status, name='toggle_client_status'),
]
