import json
import numpy as np
import cv2
from django.contrib.auth import get_user_model
from mtcnn import MTCNN
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.cache import cache
import uuid

from apps.core.models import FacialData
from kamazon import settings

User = get_user_model()


class FacialLoginConsumer(AsyncWebsocketConsumer):
    MIN_BLUR_SCORE = settings.AUTH_FACIAL_MIN_BLUR_SCORE
    MIN_BRIGHTNESS = settings.AUTH_FACIAL_MIN_BRIGHTNESS
    MAX_BRIGHTNESS = settings.AUTH_FACIAL_MAX_BRIGHTNESS
    MIN_CONTRAST = settings.AUTH_FACIAL_MIN_CONTRAST
    SIMILARITY_THRESHOLD = settings.AUTH_SIMILARITY_THRESHOLD

    async def connect(self):
        self.auth_token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'facial_auth_{self.auth_token}'
        self.detector = MTCNN()
        self.authenticated = False
        self.processing = False
        self.user_facial_data = None

        email = await self.get_email_from_token()
        if not email:
            await self.close(code=4001)
            return

        self.email = email

        user_exists = await self.check_user_and_facial_data()

        if not user_exists:
            await self.close(code=4000)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Conexión establecida. Posiciona tu rostro en el centro.',
            'status': 'ready'
        }))

    async def disconnect(self, close_code):
        await self.cleanup_auth_token()

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def cleanup_auth_token(self):
        try:
            cache.delete(f'facial_auth_{self.auth_token}')
        except Exception as e:
            logger.error(f"Error cleaning up token: {str(e)}")

    @database_sync_to_async
    def get_email_from_token(self):
        try:
            email = cache.get(f'facial_auth_{self.auth_token}')
            return email
        except Exception as e:
            logger.error(f"Error getting email from token: {str(e)}")
            return None

    @database_sync_to_async
    def check_user_and_facial_data(self):
        try:
            user = User.objects.get(email=self.email)
            facial_data = FacialData.objects.filter(user=user, is_active=True).first()

            if facial_data and facial_data.face_image:
                facial_data.face_image.seek(0)
                image_bytes = facial_data.face_image.read()
                nparr = np.frombuffer(image_bytes, np.uint8)
                self.reference_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                self.reference_image = cv2.cvtColor(self.reference_image, cv2.COLOR_BGR2RGB)
                self.user_id = user.id
                return True
            return False
        except User.DoesNotExist:
            return False
        except Exception as e:
            return False

    async def receive(self, text_data=None, bytes_data=None):
        if self.authenticated:
            return

        if self.processing:
            return

        self.processing = True

        try:
            if bytes_data:
                await self.process_frame_bytes(bytes_data)
        except Exception as e:
            await self.send_status('Error procesando frame', 'error')
        finally:
            self.processing = False

    def calculate_blur_score(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var

    def calculate_brightness(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return np.mean(gray)

    def calculate_contrast(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return np.std(gray)

    def is_well_lit(self, image):
        brightness = self.calculate_brightness(image)
        contrast = self.calculate_contrast(image)

        brightness_ok = self.MIN_BRIGHTNESS <= brightness <= self.MAX_BRIGHTNESS
        contrast_ok = contrast >= self.MIN_CONTRAST

        return brightness_ok and contrast_ok, brightness, contrast

    def compare_faces(self, current_face, reference_face):
        try:
            size = (100, 100)
            current_resized = cv2.resize(current_face, size)
            reference_resized = cv2.resize(reference_face, size)

            current_gray = cv2.cvtColor(current_resized, cv2.COLOR_RGB2GRAY)
            reference_gray = cv2.cvtColor(reference_resized, cv2.COLOR_RGB2GRAY)

            current_gray = cv2.equalizeHist(current_gray)
            reference_gray = cv2.equalizeHist(reference_gray)

            result = cv2.matchTemplate(current_gray, reference_gray, cv2.TM_CCOEFF_NORMED)
            similarity = np.max(result)

            diff = cv2.absdiff(current_gray, reference_gray)
            mse = np.mean(diff ** 2)
            structural_similarity = 1 / (1 + mse / 1000)

            final_similarity = (similarity * 0.7 + structural_similarity * 0.3)

            return final_similarity

        except Exception as e:
            return 0.0

    async def process_frame_bytes(self, image_bytes):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                await self.send_status('Frame inválido', 'invalid_frame')
                return

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = self.detector.detect_faces(rgb_image)

            if not faces:
                await self.send_status('Buscando rostro...', 'searching')
                return

            if len(faces) > 1:
                await self.send_status('Múltiples rostros detectados. Mantén solo un rostro visible.', 'multiple_faces')
                return

            face = faces[0]
            x, y, w, h = face['box']

            margin = 20
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(rgb_image.shape[1], x + w + margin)
            y2 = min(rgb_image.shape[0], y + h + margin)

            face_roi = rgb_image[y1:y2, x1:x2]

            blur_score = self.calculate_blur_score(face_roi)
            is_lit_ok, brightness_val, contrast_val = self.is_well_lit(face_roi)

            if blur_score < self.MIN_BLUR_SCORE:
                await self.send_status(f'Imagen muy borrosa. Mantén el dispositivo estable.', 'blurry')
                return

            if not is_lit_ok:
                if brightness_val < self.MIN_BRIGHTNESS:
                    await self.send_status('Muy poca luz. Busca mejor iluminación.', 'dark')
                elif brightness_val > self.MAX_BRIGHTNESS:
                    await self.send_status('Demasiada luz. Reduce la iluminación.', 'bright')
                else:
                    await self.send_status('Bajo contraste. Mejora la iluminación.', 'low_contrast')
                return

            similarity = self.compare_faces(face_roi, self.reference_image)

            await self.send_status(f'Analizando rostro... Similitud: {similarity:.2f}', 'analyzing')

            if similarity >= self.SIMILARITY_THRESHOLD:
                success_token = await self.mark_auth_success()
                if success_token:
                    self.authenticated = True
                    await self.send_status('¡Autenticación exitosa!', 'success', {'auth_token': success_token})
                else:
                    await self.send_status('Error en autenticación', 'auth_error')
            else:
                await self.send_status(f'Rostro no reconocido. Similitud: {similarity:.2f}', 'not_recognized')

        except Exception as e:
            logger.error(f"Error en process_frame_bytes: {str(e)}")
            await self.send_status('Error interno', 'error')

    @database_sync_to_async
    def mark_auth_success(self):
        try:
            success_token = str(uuid.uuid4())

            cache.set(f'facial_auth_success_{success_token}', self.user_id, timeout=120)

            return success_token

        except Exception as e:
            return None

    async def send_status(self, message, status, extra_data=None):
        data = {
            'type': 'status',
            'message': message,
            'status': status,
            'authenticated': self.authenticated
        }

        if extra_data:
            data.update(extra_data)

        await self.send(text_data=json.dumps(data))

    async def receive_json_content(self, content):
        if content.get('action') == 'reset':
            self.authenticated = False
            await self.send_status('Listo para nuevo intento', 'ready')
