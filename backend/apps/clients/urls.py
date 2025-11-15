from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Use a unique namespace for the clients app
app_name = 'clients_api'

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet, basename='client')

urlpatterns = [
    # Include ViewSet URLs
    path('', include(router.urls)),
    
    # Client statistics
    path('stats/', views.ClientStatsView.as_view(), name='client-stats'),
    
    # Client notes (nested under clients)
    path('clients/<int:client_id>/notes/', views.ClientNoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='client-note-list'),
    path('clients/<int:client_id>/notes/<int:pk>/', views.ClientNoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='client-note-detail'),
    path('clients/<int:client_id>/notes/recent/', views.ClientNoteViewSet.as_view({'get': 'recent'}), name='client-note-recent'),
]
