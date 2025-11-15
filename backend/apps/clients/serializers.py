from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Client, ClientNote

User = get_user_model()


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Client model.
    """
    full_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'address', 'city', 'state', 'postal_code', 'country',
            'date_of_birth', 'occupation', 'company', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class ClientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new clients.
    """
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'postal_code', 'country',
            'date_of_birth', 'occupation', 'company', 'is_active'
        ]
    
    def validate_email(self, value):
        """Check if email is unique for the current user."""
        if value and Client.objects.filter(
            email=value, 
            created_by=self.context['request'].user
        ).exists():
            raise serializers.ValidationError("A client with this email already exists.")
        return value


class ClientNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientNote model.
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ClientNote
        fields = [
            'id', 'client', 'title', 'content', 'created_by', 
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'created_by', 'created_at', 'updated_at']


class ClientDetailSerializer(ClientSerializer):
    """
    Detailed client serializer with additional information.
    """
    notes = ClientNoteSerializer(source='clientnote_set', many=True, read_only=True)
    appointment_count = serializers.SerializerMethodField()
    
    class Meta(ClientSerializer.Meta):
        fields = ClientSerializer.Meta.fields + ['notes', 'appointment_count']
    
    def get_appointment_count(self, obj):
        return obj.appointments.count()


class ClientStatsSerializer(serializers.Serializer):
    """
    Serializer for client statistics.
    """
    total_clients = serializers.IntegerField()
    active_clients = serializers.IntegerField()
    inactive_clients = serializers.IntegerField()
    new_clients_this_month = serializers.IntegerField()
    clients_by_city = serializers.ListField()
    
    def create(self, validated_data):
        pass
    
    def update(self, instance, validated_data):
        pass
