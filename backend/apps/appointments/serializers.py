from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for the Appointment model."""
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'title', 'description',
            'start_time', 'end_time', 'status',
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
