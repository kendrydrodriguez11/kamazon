import uuid

from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from apps.core.models import FacialData
import json

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class CheckUserFacialExistsView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()

            if not email:
                return JsonResponse({
                    'exists': False,
                    'has_facial_data': False,
                    'token': None,
                    'message': 'Email requerido'
                })

            try:
                user = User.objects.get(email=email)
                facial_data = FacialData.objects.filter(user=user, is_active=True).first()

                has_facial_data = bool(facial_data and facial_data.face_image)

                if has_facial_data:
                    auth_token = str(uuid.uuid4())

                    cache.set(f'facial_auth_{auth_token}', email, timeout=300)

                    return JsonResponse({
                        'exists': True,
                        'has_facial_data': True,
                        'token': auth_token,
                        'message': 'Usuario encontrado'
                    })
                else:
                    return JsonResponse({
                        'exists': True,
                        'has_facial_data': False,
                        'token': None,
                        'message': 'Usuario sin datos faciales'
                    })

            except User.DoesNotExist:
                return JsonResponse({
                    'exists': False,
                    'has_facial_data': False,
                    'token': None,
                    'message': 'Usuario no encontrado'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'exists': False,
                'has_facial_data': False,
                'token': None,
                'message': 'JSON inválido'
            })
        except Exception as e:
            return JsonResponse({
                'exists': False,
                'has_facial_data': False,
                'token': None,
                'message': 'Error interno'
            })
