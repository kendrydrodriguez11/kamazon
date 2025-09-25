import threading
from user_agents import parse

from apps.core.models import Device
from kamazon.fuctions import get_city_from_ip
from django.contrib.sessions.models import Session

thread_local = threading.local()


class DeviceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        thread_local.current_request = request
        response = self.get_response(request)
        if request.user.is_authenticated:
            self.update_device(request)
        return response

    def update_device(self, request):
        user = request.user
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        ip_address = request.META.get('REMOTE_ADDR', '')
        session_key = request.session.session_key
        last_activity = request.session.get('last_activity', None)
        os = user_agent.os.family
        device_type = self.get_device_type(user_agent)

        location = get_city_from_ip(ip_address)

        session = Session.objects.get(session_key=session_key)

        device, created = Device.objects.update_or_create(
            user=user,
            session=session,
            defaults={
                'ip_address': ip_address,
                'last_activity': last_activity,
                'os': os,
                'device_type': device_type,
                'location': location,
            }
        )
        if not created:
            device.last_activity = last_activity
            device.save()

    def get_device_type(self, user_agent):
        if user_agent.is_mobile:
            return 'Mobile'
        elif user_agent.is_tablet:
            return 'Tablet'
        elif user_agent.is_pc:
            return 'PC'
        return 'Other'
