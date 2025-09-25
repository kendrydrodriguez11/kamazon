from django.db import models

from apps.core.models import ModelBase, User


class Cart(ModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'