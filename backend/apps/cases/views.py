from django.db import models
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Case
from .serializers import CaseSerializer, CaseNoteSerializer

class CaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing cases.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CaseSerializer

    def get_queryset(self):
        """
        This view returns a list of all cases for the currently authenticated user.
        Users can see cases they created or are assigned to.
        """
        user = self.request.user
        return Case.objects.filter(
            models.Q(created_by=user) | 
            models.Q(assigned_to=user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        """Set the created_by field to the current user when creating a case."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to a case."""
        case = self.get_object()
        serializer = CaseNoteSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(case=case, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign_to_me(self, request, pk=None):
        """Assign the case to the current user."""
        case = self.get_object()
        case.assigned_to.add(request.user)
        return Response({'status': 'case assigned to you'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close the case."""
        case = self.get_object()
        case.status = 'closed'
        case.save()
        serializer = self.get_serializer(case)
        return Response(serializer.data)
