from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import UpdateView
from apps.settings.forms.user import UserUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

User = get_user_model()

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'pages/settings/user/detail/page.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profile'
        return context

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'pages/settings/user/update/page.html'
    success_url = reverse_lazy('settings:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your profile has been successfully updated.")
        if 'new_password' in form.cleaned_data and form.cleaned_data['new_password']:
            update_session_auth_hash(self.request, form.instance)
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profile'
        context['submit_text'] = 'Update'
        return context


class UserFaceRegisterView(LoginRequiredMixin, TemplateView):
    template_name = "pages/settings/user/facial/page.html"