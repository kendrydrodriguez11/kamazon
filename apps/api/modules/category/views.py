from django.http import JsonResponse
from django.views import View

from apps.commerce.models.category import Category


class CategoryListAPIView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()[:3]
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'image': category.get_image(),
            })
        return JsonResponse(data, safe=False)
