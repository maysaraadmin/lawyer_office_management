from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Case(models.Model):
    """Model representing a legal case."""
    
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        PENDING = 'pending', _('Pending')
        CLOSED = 'closed', _('Closed')
    
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='cases',
        verbose_name=_('client')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_cases',
        verbose_name=_('created by')
    )
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_cases',
        verbose_name=_('assigned to'),
        blank=True
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    closed_at = models.DateTimeField(_('closed at'), null=True, blank=True)

    class Meta:
        verbose_name = _('case')
        verbose_name_plural = _('cases')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class CaseNote(models.Model):
    """Model for notes related to a case."""
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('case')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='case_notes',
        verbose_name=_('author')
    )
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('case note')
        verbose_name_plural = _('case notes')
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.case.title} by {self.author}"
