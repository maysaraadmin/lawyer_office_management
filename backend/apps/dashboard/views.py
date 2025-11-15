from django.shortcuts import render
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from apps.clients.models import Client, ClientNote
from apps.appointments.models import Appointment
from .models import DashboardStats, RecentActivity
from .serializers import (
    DashboardSerializer, 
    DashboardStatsSerializer,
    RecentActivitySerializer,
    ClientSummarySerializer,
    AppointmentSummarySerializer,
    UserProfileSerializer
)

User = get_user_model()


class DashboardView(APIView):
    """Main dashboard view with statistics and overview data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Get statistics
        total_clients = Client.objects.filter(created_by=user).count()
        total_appointments = Appointment.objects.filter(user=user).count()
        
        # Appointment statistics
        upcoming_appointments = Appointment.objects.filter(
            user=user,
            start_time__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).count()
        
        completed_appointments = Appointment.objects.filter(
            user=user,
            status='completed'
        ).count()
        
        cancelled_appointments = Appointment.objects.filter(
            user=user,
            status='cancelled'
        ).count()
        
        # New clients this month
        new_clients_this_month = Client.objects.filter(
            created_by=user,
            created_at__gte=start_of_month
        ).count()
        
        # Recent clients
        recent_clients = Client.objects.filter(
            created_by=user
        ).order_by('-created_at')[:5]
        
        # Upcoming appointments
        upcoming_appointments_list = Appointment.objects.filter(
            user=user,
            start_time__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('start_time')[:5]
        
        # Recent activities
        recent_activities = RecentActivity.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        # User info
        user_info = UserProfileSerializer(user).data
        
        dashboard_data = {
            'total_clients': total_clients,
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'new_clients_this_month': new_clients_this_month,
            'recent_clients': ClientSummarySerializer(recent_clients, many=True).data,
            'upcoming_appointments_list': AppointmentSummarySerializer(upcoming_appointments_list, many=True).data,
            'recent_activities': RecentActivitySerializer(recent_activities, many=True).data,
            'user_info': user_info
        }
        
        return Response(dashboard_data)


class DashboardStatsView(generics.ListAPIView):
    """View for historical dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DashboardStatsSerializer

    def get_queryset(self):
        return DashboardStats.objects.filter(
            user=self.request.user
        ).order_by('-stat_date')[:30]  # Last 30 days


class RecentActivityView(generics.ListCreateAPIView):
    """View for recent user activities"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RecentActivitySerializer

    def get_queryset(self):
        return RecentActivity.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:50]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileView(APIView):
    """Enhanced user profile view"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivityChartView(APIView):
    """View for appointment activity chart data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get appointments grouped by date
        appointments = Appointment.objects.filter(
            user=user,
            start_time__gte=start_date
        ).extra(
            select={'day': 'date(start_time)'}
        ).values('day').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled'))
        ).order_by('day')
        
        return Response(list(appointments))


class ClientGrowthView(APIView):
    """View for client growth chart data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get new clients grouped by date
        clients = Client.objects.filter(
            created_by=user,
            created_at__gte=start_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            new_clients=Count('id')
        ).order_by('day')
        
        return Response(list(clients))
