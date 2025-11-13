from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Use a unique namespace for the cases app
app_name = 'cases_api'

router = DefaultRouter()
router.register(r'cases', views.CaseViewSet, basename='case')

# Additional URL patterns can be added here
urlpatterns = [
    path('', include(router.urls)),
]
