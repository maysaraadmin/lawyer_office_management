from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    """
    Inline admin for InvoiceItem model.
    """
    model = InvoiceItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('description', 'quantity', 'unit_price', 'tax_rate', 'amount', 'created_at', 'updated_at')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Invoice model.
    """
    list_display = ('invoice_number', 'client', 'issue_date', 'due_date', 'status', 'total')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'client__first_name', 'client__last_name')
    date_hierarchy = 'issue_date'
    ordering = ('-issue_date', '-created_at')
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'client', 'case', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_at')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'total')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InvoiceItemInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for the InvoiceItem model.
    """
    list_display = ('description', 'invoice', 'quantity', 'unit_price', 'amount')
    list_filter = ('invoice__status',)
    search_fields = ('description', 'invoice__invoice_number')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Item Details', {
            'fields': ('invoice', 'description', 'quantity', 'unit_price', 'tax_rate', 'amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
