from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget

from apps.commerce.models.product import Product

User = get_user_model()

class ProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['user', 'created_at', 'updated_at', 'views']
        widgets = {
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        stock = cleaned_data.get("stock")

        if price < 0:
            raise ValidationError("The price must be greater than or equal to zero.")

        if stock < 0:
            raise ValidationError("The stock must be greater than or equal to zero.")

        return cleaned_data