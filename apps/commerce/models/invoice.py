from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import ModelBase

User = get_user_model()


class Invoice(ModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invoice {self.id}'

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        db_table = 'invoices'
