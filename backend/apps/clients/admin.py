from django.contrib import admin
from .models import Client, ClientDocument, ClientNote

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin interface for the Client model.
    """
    list_display = ('first_name', 'last_name', 'email', 'phone', 'is_active')
    list_filter = ('is_active', 'city', 'state', 'country')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('last_name', 'first_name')

@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for the ClientDocument model.
    """
    list_display = ('title', 'client', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'client__first_name', 'client__last_name')
    list_per_page = 20
    date_hierarchy = 'uploaded_at'
    raw_id_fields = ('client', 'uploaded_by')

@admin.register(ClientNote)
class ClientNoteAdmin(admin.ModelAdmin):
    """
    Admin interface for the ClientNote model.
    """
    list_display = ('title', 'client', 'created_by', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'client__first_name', 'client__last_name')
    list_per_page = 20
    date_hierarchy = 'created_at'
    raw_id_fields = ('client', 'created_by')
