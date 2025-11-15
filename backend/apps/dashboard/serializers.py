from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.appointments.models import Appointment
from .models import DashboardStats, RecentActivity

User = get_user_model()


class DashboardStatsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard statistics"""
    
    class Meta:
        model = DashboardStats
        fields = '__all__'


class RecentActivitySerializer(serializers.ModelSerializer):
    """Serializer for recent activities"""
    
    class Meta:
        model = RecentActivity
        fields = '__all__'


class ClientSummarySerializer(serializers.ModelSerializer):
    """Lightweight client serializer for dashboard"""
    
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']


class AppointmentSummarySerializer(serializers.ModelSerializer):
    """Lightweight appointment serializer for dashboard"""
    client_name = serializers.CharField(source='client.first_name', read_only=True)
    client_last_name = serializers.CharField(source='client.last_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'title', 'start_time', 'end_time', 'status', 'client_name', 'client_last_name']


class DashboardSerializer(serializers.Serializer):
    """Main dashboard serializer combining all data"""
    
    # Statistics
    total_clients = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    new_clients_this_month = serializers.IntegerField()
    
    # Recent data
    recent_clients = ClientSummarySerializer(many=True)
    upcoming_appointments_list = AppointmentSummarySerializer(many=True)
    recent_activities = RecentActivitySerializer(many=True)
    
    # User info
    user_info = serializers.DictField()


class UserProfileSerializer(serializers.ModelSerializer):
    """Enhanced user profile serializer for dashboard"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 
                 'user_type', 'phone', 'address', 'date_of_birth']
        read_only_fields = ['id', 'email']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
