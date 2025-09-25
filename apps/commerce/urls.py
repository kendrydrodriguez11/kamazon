from django.urls import path, include

app_name = 'commerce'

urlpatterns = [
    path('authentication/', include('apps.commerce.modules.authentication.urls')),
    path('cart/', include('apps.commerce.modules.cart.urls')),
    path('products/', include('apps.commerce.modules.product.urls')),
    path('categories/', include('apps.commerce.modules.category.urls')),
]
