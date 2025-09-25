from django.urls import path

from apps.commerce.modules.cart.views import CartDetailView, CartCheckoutView

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('checkout/', CartCheckoutView.as_view(), name='cart-checkout'),
]
