from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import Case, CaseNote

class CaseNoteSerializer(serializers.ModelSerializer):
    """Serializer for the CaseNote model."""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = CaseNote
        fields = ['id', 'content', 'author', 'author_name', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

class CaseSerializer(serializers.ModelSerializer):
    """Serializer for the Case model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notes = CaseNoteSerializer(many=True, read_only=True)
    assigned_to_names = serializers.SerializerMethodField()
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'description', 'client', 'client_name',
            'status', 'status_display', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_names', 'notes',
            'created_at', 'updated_at', 'closed_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'closed_at']

    def get_assigned_to_names(self, obj):
        """
        Get the full names of all users assigned to the case.
        """
        return [user.get_full_name() for user in obj.assigned_to.all()]

    def update(self, instance, validated_data):
        """
        Update the case instance and handle status changes.
        """
        # If status is being updated to 'closed', set the closed_at timestamp
        if 'status' in validated_data and validated_data['status'] == 'closed':
            instance.closed_at = timezone.now()
        
        return super().update(instance, validated_data)
