from django.views.generic import ListView

from apps.commerce.models.category import Category


class CategoryListView(ListView):
    model = Category
    template_name = 'pages/category/list/page.html'
    context_object_name = 'categories'
    paginate_by = 12