from decimal import Decimal

from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.commerce.models.cart import Cart
from apps.commerce.models.cart_item import CartItem
from kamazon import settings


class CartDetailView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'pages/cart/detail/page.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = context['cart_items']

        subtotal = sum(item.get_subtotal() for item in cart_items)
        tax_rate = Decimal(settings.COMMERCE_TAX_RATE)
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        context['subtotal'] = subtotal
        context['tax_rate'] = tax_rate * 100
        context['tax_amount'] = tax_amount
        context['total'] = total
        return context


class CartCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/cart/checkout/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return redirect('commerce:cart-detail')

        subtotal = sum(item.get_subtotal() for item in cart_items)
        tax_rate = Decimal(settings.COMMERCE_TAX_RATE)
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        context['cart_items'] = cart_items
        context['subtotal'] = subtotal
        context['tax_rate'] = tax_rate * 100
        context['tax_amount'] = tax_amount
        context['total'] = total
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context
