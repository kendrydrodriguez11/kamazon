from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect

from apps.commerce.modules.authentication.forms.login import LoginForm
from apps.commerce.modules.authentication.forms.register import RegisterForm

User = get_user_model()


class AuthRegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'pages/authentication/register/page.html'
    success_url = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        context['submit_text'] = 'Register'
        return context


class AuthLoginView(LoginView):
    template_name = 'pages/authentication/login/page.html'
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        context['submit_text'] = 'Login'
        return context


@login_required
def AuthLogoutView(request):
    logout(request)
    return redirect('home')
