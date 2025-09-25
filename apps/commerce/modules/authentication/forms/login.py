from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'remember_me']