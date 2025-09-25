from django.urls import path

from apps.api.modules.product.views import ProductListAPIView, ProductDetailAPIView, ProductRecommendAPIView, \
    RecentAddedProductListAPIView

urlpatterns = [
    path('list/', ProductListAPIView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('recommended', ProductRecommendAPIView.as_view(), name='product-recommend'),
    path('recent-added/', RecentAddedProductListAPIView.as_view(), name='product-recent-added'),
]