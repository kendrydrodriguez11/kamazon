from django.contrib import admin

from apps.commerce.models.category import Category
from apps.commerce.models.product import Product

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)