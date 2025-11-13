from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Invoice(models.Model):
    """
    Model representing an invoice.
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        SENT = 'sent', _('Sent')
        PAID = 'paid', _('Paid')
        OVERDUE = 'overdue', _('Overdue')
        CANCELLED = 'cancelled', _('Cancelled')
    
    invoice_number = models.CharField(_('invoice number'), max_length=50, unique=True)
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('client')
    )
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('case')
    )
    issue_date = models.DateField(_('issue date'))
    due_date = models.DateField(_('due date'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    subtotal = models.DecimalField(_('subtotal'), max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=12, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=12, decimal_places=2)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    paid_at = models.DateTimeField(_('paid at'), null=True, blank=True)

    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client}"


class InvoiceItem(models.Model):
    """
    Model representing an item on an invoice.
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('invoice')
    )
    description = models.CharField(_('description'), max_length=200)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(_('unit price'), max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('invoice item')
        verbose_name_plural = _('invoice items')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.description} - {self.amount}"
