from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows appointments to be viewed or edited.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all appointments
        for the currently authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-start_time')

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
