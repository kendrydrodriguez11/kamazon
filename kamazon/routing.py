from django.urls import path

from kamazon.consumers.facial_login import FacialLoginConsumer
from kamazon.consumers.facial_register import FacialRegisterConsumer
from kamazon.consumers.qr_login import QRLoginConsumer

websocket_urlpatterns = [
    path("ws/qr/<str:token>/", QRLoginConsumer.as_asgi()),
    path("ws/facial-register/<str:user_id>/", FacialRegisterConsumer.as_asgi()),
    path("ws/facial-login/<str:token>/", FacialLoginConsumer.as_asgi()),
]
