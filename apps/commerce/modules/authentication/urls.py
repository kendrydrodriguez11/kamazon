from django.urls import path

from apps.commerce.modules.authentication.views import AuthLoginView, AuthRegisterView, AuthLogoutView
urlpatterns = [
    path('register/', AuthRegisterView.as_view(), name='authentication-register'),
    path('login/', AuthLoginView.as_view(), name='authentication-login'),
    path('logout/', AuthLogoutView, name='authentication-logout'),
]