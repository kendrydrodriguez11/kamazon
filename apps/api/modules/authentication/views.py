import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

User = get_user_model()


class AuthQRLoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        session_key = data['session_key']
        try:
            session = Session.objects.get(session_key=session_key)
        except Session.DoesNotExist:
            return JsonResponse({'message': 'Invalid session key'}, status=400)
        if session.expire_date < timezone.now():
            return JsonResponse({'message': 'Session has expired'}, status=400)
        user_id = session.get_decoded().get('_auth_user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid user'}, status=400)
        login(request, user)
        return JsonResponse({'message': 'Login successful'})


class AuthFacialLoginView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            auth_token = data.get('auth_token', '').strip()
            if not auth_token:
                return JsonResponse({'success': False, 'message': 'Token requerido'})

            user_id = cache.get(f'facial_auth_success_{auth_token}')

            if not user_id:
                return JsonResponse({'success': False, 'message': 'Token inválido o expirado'})

            try:
                user = User.objects.get(id=user_id)

                login(request, user)

                cache.delete(f'facial_auth_success_{auth_token}')
                cache.delete(f'facial_auth_{auth_token}')

                return JsonResponse({'success': True, 'message': 'Login exitoso'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Usuario no encontrado'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error interno'})


class SendAuthorizedMessageDevice(LoginRequiredMixin, View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            if not data:
                raise KeyError("data is missing")

            token = data['token']
            cache_data = cache.get(token)

            if cache_data is None:
                return JsonResponse({'success': False, 'message': 'Invalid token'}, status=400)

            user_id = request.user.id
            cache_data['user_id'] = user_id
            cache.set(token, cache_data, timeout=600)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                token,
                {
                    'type': 'handle_receive',
                    'user_id': user_id
                }
            )
            return JsonResponse({'success': True, 'message': 'Message sent'})
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
        except KeyError as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
