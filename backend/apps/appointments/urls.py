from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Use a unique namespace for the appointments app
app_name = 'appointments_api'

router = DefaultRouter()
router.register(r'', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
