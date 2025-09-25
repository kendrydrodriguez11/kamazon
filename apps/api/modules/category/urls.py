from django.urls import path

from apps.api.modules.category.views import CategoryListAPIView

urlpatterns = [
    path('list/', CategoryListAPIView.as_view(), name='categories-list'),
]