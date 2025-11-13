from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Client
from .serializers import ClientSerializer, ClientDocumentSerializer, ClientNoteSerializer

class ClientListView(generics.ListCreateAPIView):
    """
    View for listing and creating clients.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a client.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

class ClientStatsView(APIView):
    """
    View for client statistics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        total_clients = Client.objects.count()
        active_clients = Client.objects.filter(is_active=True).count()
        
        return Response({
            'total_clients': total_clients,
            'active_clients': active_clients,
        })

class ClientDocumentListView(generics.ListCreateAPIView):
    """
    View for listing and creating client documents.
    """
    serializer_class = ClientDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return ClientDocument.objects.filter(client_id=client_id)
    
    def perform_create(self, serializer):
        client = get_object_or_404(Client, id=self.kwargs.get('client_id'))
        serializer.save(client=client, uploaded_by=self.request.user)

class ClientDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a client document.
    """
    serializer_class = ClientDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ClientDocument.objects.filter(client_id=self.kwargs.get('client_id'))
    
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        return obj

class ClientNoteListView(generics.ListCreateAPIView):
    """
    View for listing and creating client notes.
    """
    serializer_class = ClientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return ClientNote.objects.filter(client_id=client_id)
    
    def perform_create(self, serializer):
        client = get_object_or_404(Client, id=self.kwargs.get('client_id'))
        serializer.save(client=client, created_by=self.request.user)

class ClientNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a client note.
    """
    serializer_class = ClientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ClientNote.objects.filter(client_id=self.kwargs.get('client_id'))
    
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        return obj
