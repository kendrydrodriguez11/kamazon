from django.urls import path

from apps.api.modules.cart.views import AddToCartView, RemoveFromCartView, CreatePaymentIntentView, PaymentSuccessView

urlpatterns = [
    path('add/<int:product_id>/', AddToCartView.as_view(), name='cart-add-item'),
    path('remove/<int:item_id>/', RemoveFromCartView.as_view(), name='cart-remove-item'),
    path('payment/create', CreatePaymentIntentView.as_view(), name='cart-payment-create'),
    path('payment/success', PaymentSuccessView.as_view(), name='cart-payment-success'),
]