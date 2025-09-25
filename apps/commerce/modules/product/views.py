from django.views.generic import DetailView
from django_filters.views import FilterView

from apps.commerce.models.category import Category
from apps.commerce.models.product import Product
from apps.commerce.modules.product.filters import ProductFilter


class ProductListView(FilterView):
    model = Product
    template_name = 'pages/product/list/page.html'
    context_object_name = 'products'
    filterset_class = ProductFilter
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                context['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'pages/product/detail/page.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj
