from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.commerce.models.cart import Cart

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        Cart.objects.get_or_create(user=obj)
