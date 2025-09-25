import json
from decimal import Decimal

import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from apps.commerce.models.cart import Cart
from apps.commerce.models.cart_item import CartItem
from apps.commerce.models.invoice import Invoice
from apps.commerce.models.invoice_detail import InvoiceDetail
from apps.commerce.models.product import Product

from kamazon import settings


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        cart = Cart.objects.get(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.quantity = 1
            cart_item.save()

        return redirect('commerce:product-detail', product_id)


class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return redirect('commerce:cart-detail')


class CreatePaymentIntentView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return JsonResponse({'error': 'Carrito vacío'}, status=400)

            subtotal = sum(item.get_subtotal() for item in cart_items)
            tax_rate = Decimal(settings.COMMERCE_TAX_RATE)
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount

            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency='usd',
                metadata={
                    'user_id': request.user.id,
                    'cart_id': cart.id,
                }
            )

            return JsonResponse({
                'client_secret': intent.client_secret
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class PaymentSuccessView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')

            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart).select_related('product')

                if not cart_items.exists():
                    return JsonResponse({'error': 'El carrito está vacío'}, status=400)

                subtotal = sum(item.get_subtotal() for item in cart_items)
                tax_rate = Decimal(settings.COMMERCE_TAX_RATE)
                tax_amount = subtotal * tax_rate
                total = subtotal + tax_amount

                invoice = Invoice.objects.create(
                    user=request.user,
                    subtotal=subtotal,
                    tax_rate=tax_rate,
                    tax_amount=tax_amount,
                    total=total
                )

                for cart_item in cart_items:
                    InvoiceDetail.objects.create(
                        invoice=invoice,
                        description=cart_item.product.name,
                        unit_price=cart_item.product.price,
                        quantity=cart_item.quantity,
                        amount=cart_item.get_subtotal()
                    )

                cart_items.delete()

                return JsonResponse({
                    'success': True,
                    'invoice_id': invoice.id,
                    'invoice_total': str(invoice.total)
                })
            else:
                return JsonResponse({'error': 'Pago no confirmado'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
