from django.urls import path
from . import views

# Use a unique namespace for the clients app
app_name = 'clients_api'

urlpatterns = [
    # Client endpoints
    path('', views.ClientListView.as_view(), name='client-list'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('stats/', views.ClientStatsView.as_view(), name='client-stats'),
    
    # Client notes endpoints
    path('<int:client_id>/notes/', views.ClientNoteListView.as_view(), name='client-note-list'),
    path('<int:client_id>/notes/<int:pk>/', views.ClientNoteDetailView.as_view(), name='client-note-detail'),
]
