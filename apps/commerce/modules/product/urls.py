from django.urls import path

from apps.commerce.modules.product.views import ProductListView, ProductDetailView

urlpatterns = [
    path('', ProductListView.as_view(), name='products-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
