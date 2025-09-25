from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('category/', include('apps.api.modules.category.urls')),
    path('product/', include('apps.api.modules.product.urls')),
    path('authentication/', include('apps.api.modules.authentication.urls')),
    path('user/', include('apps.api.modules.user.urls')),
    path('cart/', include('apps.api.modules.cart.urls')),
]
