from django.urls import path

from apps.commerce.modules.category.views import CategoryListView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
]