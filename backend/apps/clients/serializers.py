from rest_framework import serializers
from .models import Client, ClientDocument, ClientNote
from apps.users.serializers import UserSerializer

class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Client model.
    """
    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'postal_code', 'country',
            'date_of_birth', 'occupation', 'company', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClientDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientDocument model.
    """
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ClientDocument
        fields = [
            'id', 'client', 'title', 'description', 'document',
            'document_type', 'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['id', 'client', 'uploaded_by', 'uploaded_at']
        extra_kwargs = {
            'document': {'required': True}
        }

class ClientNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientNote model.
    """
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ClientNote
        fields = [
            'id', 'client', 'title', 'content', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'created_by', 'created_at', 'updated_at']

class ClientStatsSerializer(serializers.Serializer):
    """
    Serializer for client statistics.
    """
    total_clients = serializers.IntegerField()
    active_clients = serializers.IntegerField()
    
    def create(self, validated_data):
        pass
    
    def update(self, instance, validated_data):
        pass
