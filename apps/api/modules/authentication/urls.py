from django.urls import path

from apps.api.modules.authentication.views import AuthQRLoginView, SendAuthorizedMessageDevice, AuthFacialLoginView

urlpatterns = [
    path("login/qr/", AuthQRLoginView.as_view(), name='authentication-qrlogin'),
    path("login/facial/", AuthFacialLoginView.as_view(), name='authentication-facial-login'),
    path('devices/authorize/', SendAuthorizedMessageDevice.as_view(), name='device-authorize'),
]