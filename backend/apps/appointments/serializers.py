from rest_framework import serializers
from .models import Appointment
from apps.clients.serializers import ClientSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for the Appointment model."""
    
    client_name = serializers.CharField(source='client.first_name', read_only=True)
    client_last_name = serializers.CharField(source='client.last_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    client_details = ClientSerializer(source='client', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'client', 'client_name', 'client_last_name', 
            'client_email', 'client_details', 'title', 'description',
            'start_time', 'end_time', 'status', 'location', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
        extra_kwargs = {
            'start_time': {'required': True},
            'end_time': {'required': True},
        }

    def validate(self, data):
        """
        Check that start_time is before end_time.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments with client info"""
    
    class Meta:
        model = Appointment
        fields = [
            'client', 'title', 'description',
            'start_time', 'end_time', 'location', 'notes'
        ]
        extra_kwargs = {
            'start_time': {'required': True},
            'end_time': {'required': True},
        }

    def validate(self, data):
        """
        Check that start_time is before end_time.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data
