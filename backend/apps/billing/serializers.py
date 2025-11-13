from rest_framework import serializers
from .models import Invoice, InvoiceItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the InvoiceItem model.
    """
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'tax_rate', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Invoice model.
    """
    items = InvoiceItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    case_title = serializers.CharField(source='case.title', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_name', 'case', 'case_title',
            'issue_date', 'due_date', 'status', 'status_display', 'subtotal',
            'tax_amount', 'total', 'notes', 'items', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'paid_at']

    def create(self, validated_data):
        # Handle nested creation of invoice items if needed
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice
