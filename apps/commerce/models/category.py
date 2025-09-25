from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import ModelBase

User = get_user_model()


class Category(ModelBase):
    name = models.CharField(verbose_name='Name', max_length=50, unique=True)
    image = models.ImageField(verbose_name='Image', upload_to='categories', null=True, blank=True)
    description = models.TextField(verbose_name='Description')

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return self.image.url
        return '/static/img/default-category.png'

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
        db_table = 'categories'
