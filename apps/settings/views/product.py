from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from apps.commerce.models.product import Product
from apps.settings.forms.product import ProductForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'pages/settings/products/list/page.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'pages/settings/products/add/page.html'
    success_url = reverse_lazy('settings:profile-products')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Product'
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'pages/settings/products/add/page.html'
    success_url = reverse_lazy('settings:profile-products')

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Product'
        context['submit_text'] = 'Update'
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'pages/settings/products/delete/page.html'
    success_url = reverse_lazy('settings:profile-products')

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Product'
        context['submit_text'] = 'Delete'
        return context
