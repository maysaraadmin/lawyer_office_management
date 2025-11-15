from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer

User = get_user_model()


class AppointmentStatsView(APIView):
    """Get appointment statistics"""
    
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Basic stats
        total = Appointment.objects.filter(user=request.user).count()
        today_count = Appointment.objects.filter(
            user=request.user,
            start_time__gte=today_start,
            start_time__lt=today_end
        ).count()
        
        # Upcoming in next 7 days
        next_week = now + timedelta(days=7)
        upcoming = Appointment.objects.filter(
            user=request.user,
            start_time__gte=now,
            start_time__lte=next_week
        ).count()
        
        # Completed appointments
        completed = Appointment.objects.filter(
            user=request.user,
            status='completed'
        ).count()
        
        # Active clients (clients with appointments)
        active_clients = Appointment.objects.filter(
            user=request.user
        ).values('client').distinct().count()
        
        return Response({
            'total': total,
            'today': today_count,
            'upcoming': upcoming,
            'completed': completed,
            'active_clients': active_clients,
            'total_revenue': 0.0,  # TODO: Calculate from billing
        })


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows appointments to be viewed or edited.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action."""
        if self.action == 'create':
            return AppointmentCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        """
        This view should return a list of all appointments
        for the currently authenticated user.
        """
        queryset = self.queryset.filter(user=self.request.user)
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        # Filter by client if provided
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        return queryset.order_by('-start_time')

    def perform_create(self, serializer):
        """Set the user to the current user when creating an appointment."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Custom action to confirm an appointment."""
        appointment = self.get_object()
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save()
        return Response({'status': 'appointment confirmed'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Custom action to cancel an appointment."""
        appointment = self.get_object()
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        return Response({'status': 'appointment cancelled'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Custom action to mark an appointment as completed."""
        appointment = self.get_object()
        appointment.status = Appointment.Status.COMPLETED
        appointment.save()
        return Response({'status': 'appointment completed'})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments for the current user."""
        upcoming_appointments = self.get_queryset().filter(
            start_time__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('start_time')
        
        serializer = self.get_serializer(upcoming_appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get appointments for today."""
        today = timezone.now().date()
        today_appointments = self.get_queryset().filter(
            start_time__date=today
        ).order_by('start_time')
        
        serializer = self.get_serializer(today_appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get appointments in calendar format."""
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Both start and end date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointments = self.get_queryset().filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).order_by('start_time')
        
        calendar_data = []
        for appointment in appointments:
            calendar_data.append({
                'id': appointment.id,
                'title': appointment.title,
                'start': appointment.start_time,
                'end': appointment.end_time,
                'status': appointment.status,
                'client_name': f"{appointment.client.first_name} {appointment.client.last_name}" if appointment.client else 'No Client',
                'location': appointment.location,
                'description': appointment.description
            })
        
        return Response(calendar_data)
