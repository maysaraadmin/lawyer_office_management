from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Client(models.Model):
    """Client model for storing client information."""
    
    class Meta:
        app_label = 'clients'
    
    # Basic Information
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    
    # Address Information
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state/province'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    
    # Additional Information
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    occupation = models.CharField(_('occupation'), max_length=100, blank=True)
    company = models.CharField(_('company'), max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(_('active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Returns the client's full name."""
        return f"{self.first_name} {self.last_name}"



class ClientNote(models.Model):
    """Model for storing notes related to a client."""
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('client')
    )
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='client_notes',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('client note')
        verbose_name_plural = _('client notes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.full_name}"
