from django.urls import path

from apps.api.modules.user.views import CheckUserFacialExistsView

urlpatterns = [
    path('check-user-facial/', CheckUserFacialExistsView.as_view(), name='check_user_facial_exists'),
]