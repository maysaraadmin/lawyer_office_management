from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

# Uncomment and update when models are created
# from .models import Invoice, InvoiceItem
# from .serializers import InvoiceSerializer, InvoiceItemSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing invoices.
    """
    permission_classes = [IsAuthenticated]
    # Add your queryset and serializer_class here
    # queryset = Invoice.objects.all()
    # serializer_class = InvoiceSerializer

    def get_queryset(self):
        """
        This view should return a list of all invoices
        for the currently authenticated user.
        """
        return super().get_queryset().filter(created_by=self.request.user)

    def perform_create(self, serializer):
        """Set the created_by field to the current user when creating an invoice."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark an invoice as paid."""
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_to_client(self, request, pk=None):
        """Send the invoice to the client."""
        invoice = self.get_object()
        # Add logic to send the invoice to the client
        return Response({'status': 'invoice sent to client'})
