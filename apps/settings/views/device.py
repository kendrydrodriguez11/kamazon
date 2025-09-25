from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.core.models import Device
from django.views import View
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'pages/settings/devices/list/page.html'
    context_object_name = 'devices'
    paginate_by = 10

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user).order_by('-last_activity')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_device_session_key = self.request.session.session_key
        current_device = Device.objects.filter(session__session_key=current_device_session_key).first()
        context['title'] = 'Devices'
        context['current_device'] = current_device
        return context


class ForceLogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        device = Device.objects.get(id=device_id)
        if device.user == request.user:
            Session.objects.filter(session_key=device.session.session_key).delete()
            device.delete()
        return redirect(reverse_lazy('settings:profile-devices'))


class QRScanView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/settings/devices/scan/page.html'
