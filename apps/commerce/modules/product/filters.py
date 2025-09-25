import django_filters
from django import forms

from apps.commerce.models.product import Product
from apps.commerce.models.category import Category


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={
        'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-kamazon-teal focus:border-transparent',
        'placeholder': 'Buscar productos...'
    }), required=False)

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', widget=forms.NumberInput(attrs={
        'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-kamazon-teal focus:border-transparent',
        'placeholder': 'Mínimo'
    }), required=False)

    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', widget=forms.NumberInput(attrs={
        'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-kamazon-teal focus:border-transparent',
        'placeholder': 'Máximo'
    }), required=False)

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.HiddenInput(),
        method='filter_category',
        required=False
    )

    in_stock = django_filters.BooleanFilter(
        field_name='stock',
        method='filter_in_stock',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-5 w-5 text-kamazon-teal rounded'
        }),
        required=False
    )

    order_by = django_filters.ChoiceFilter(
        choices=(
            ('price', 'Precio de menor a mayor'),
            ('-price', 'Precio de mayor a menor'),
            ('-created_at', 'Más recientes primero'),
            ('-views', 'Más populares'),
        ),
        empty_label='Ordenar por',
        method='filter_order_by',
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-kamazon-teal focus:border-transparent'
        }),
        required=False
    )

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_order_by(self, queryset, name, value):
        if value:
            return queryset.order_by(value)
        return queryset

    def filter_category(self, queryset, name, value):
        if value:
            return queryset.filter(categories=value)
        return queryset

    class Meta:
        model = Product
        fields = ['name', 'category', 'min_price', 'max_price', 'in_stock']
