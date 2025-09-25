from django.http import JsonResponse
from django.views import View

from apps.commerce.models.product import Product


class ProductDetailAPIView(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['pk'])
        data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock': product.stock,
            'description': product.description,
            'image': product.get_image(),
        }
        return JsonResponse(data)


class ProductListAPIView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        data = []
        for product in products:
            data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock,
                'description': product.description,
                'image': product.get_image(),
            })
        return JsonResponse(data, safe=False)


class ProductRecommendAPIView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-views')[:3]
        data = []
        for product in products:
            data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock,
                'description': product.description,
                'image': product.get_image(),
            })
        return JsonResponse(data, safe=False)


class RecentAddedProductListAPIView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-created_at')[:3]
        data = []
        for product in products:
            data.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock,
                'description': product.description,
                'image': product.get_image(),
            })
        return JsonResponse(data, safe=False)
