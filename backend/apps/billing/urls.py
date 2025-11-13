from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Use a unique namespace for the billing app
app_name = 'billing_api'

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
]
