from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone

from .models import Client, ClientNote
from .serializers import ClientSerializer, ClientNoteSerializer, ClientCreateSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for client CRUD operations with enhanced functionality.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action."""
        if self.action == 'create':
            return ClientCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        """
        This view should return a list of all clients
        for the currently authenticated user.
        """
        queryset = self.queryset.filter(created_by=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Filter by status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        return queryset.order_by('last_name', 'first_name')

    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a client."""
        client = self.get_object()
        client.is_active = True
        client.save()
        return Response({'status': 'client activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a client."""
        client = self.get_object()
        client.is_active = False
        client.save()
        return Response({'status': 'client deactivated'})

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Get all appointments for a specific client."""
        client = self.get_object()
        appointments = client.appointments.all().order_by('-start_time')
        
        from apps.appointments.serializers import AppointmentSerializer
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def notes_summary(self, request, pk=None):
        """Get a summary of notes for a client."""
        client = self.get_object()
        notes = client.notes.all().order_by('-created_at')
        
        summary = {
            'total_notes': notes.count(),
            'recent_notes': ClientNoteSerializer(notes[:5], many=True).data
        }
        return Response(summary)


class ClientStatsView(APIView):
    """
    Enhanced view for client statistics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        total_clients = Client.objects.filter(created_by=user).count()
        active_clients = Client.objects.filter(created_by=user, is_active=True).count()
        inactive_clients = total_clients - active_clients
        
        # New clients this month
        start_of_month = timezone.now().date().replace(day=1)
        new_clients_this_month = Client.objects.filter(
            created_by=user,
            created_at__gte=start_of_month
        ).count()
        
        # Clients by city
        clients_by_city = Client.objects.filter(
            created_by=user
        ).values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': inactive_clients,
            'new_clients_this_month': new_clients_this_month,
            'clients_by_city': list(clients_by_city)
        })


class ClientNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for client notes CRUD operations.
    """
    serializer_class = ClientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return notes for the specified client."""
        client_id = self.kwargs.get('client_id')
        return ClientNote.objects.filter(client_id=client_id)

    def perform_create(self, serializer):
        """Set the client and created_by fields."""
        client = get_object_or_404(Client, id=self.kwargs.get('client_id'))
        serializer.save(client=client, created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request, client_id=None):
        """Get recent notes for the client."""
        notes = self.get_queryset().order_by('-created_at')[:5]
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
