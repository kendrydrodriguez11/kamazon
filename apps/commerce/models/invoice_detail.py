from django.db import models

from apps.core.models import ModelBase

from apps.commerce.models.invoice import Invoice


class InvoiceDetail(ModelBase):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} (Invoice #{self.invoice.id})"

    class Meta:
        verbose_name = 'Invoice Detail'
        verbose_name_plural = 'Invoice Details'
        db_table = 'invoice_details'
