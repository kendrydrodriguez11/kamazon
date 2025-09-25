import json
import numpy as np
import cv2
from django.contrib.auth import get_user_model
from mtcnn import MTCNN
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile

from apps.core.models import FacialData
from kamazon import settings

User = get_user_model()


class FacialRegisterConsumer(AsyncWebsocketConsumer):
    MIN_BLUR_SCORE = settings.AUTH_FACIAL_MIN_BLUR_SCORE
    MIN_BRIGHTNESS = settings.AUTH_FACIAL_MIN_BRIGHTNESS
    MAX_BRIGHTNESS = settings.AUTH_FACIAL_MAX_BRIGHTNESS
    MIN_CONTRAST = settings.AUTH_FACIAL_MIN_CONTRAST

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'facial_register_{self.user_id}'
        self.detector = MTCNN()
        self.face_registered = False
        self.processing = False

        self.best_frame = None
        self.best_score = 0
        self.frame_count = 0
        self.max_frames_to_analyze = 10

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Conexión establecida. Posiciona tu rostro en el centro con buena iluminación.',
            'status': 'ready'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if self.face_registered:
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

    def calculate_quality_score(self, face_roi):
        blur_score = self.calculate_blur_score(face_roi)
        brightness = self.calculate_brightness(face_roi)
        contrast = self.calculate_contrast(face_roi)

        optimal_brightness = 140
        brightness_score = 1 - abs(brightness - optimal_brightness) / 255

        contrast_score = min(contrast / 100, 1)

        total_score = (blur_score * 0.5 + brightness_score * 100 * 0.3 + contrast_score * 100 * 0.2)

        return total_score, blur_score, brightness, contrast

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

            quality_score, blur_score, brightness, contrast = self.calculate_quality_score(face_roi)
            is_lit_ok, brightness_val, contrast_val = self.is_well_lit(face_roi)

            self.frame_count += 1

            if blur_score < self.MIN_BLUR_SCORE:
                await self.send_status(
                    f'Imagen muy borrosa. Mantén el dispositivo estable. (Nitidez: {blur_score:.1f})', 'blurry')
                return

            if not is_lit_ok:
                if brightness_val < self.MIN_BRIGHTNESS:
                    await self.send_status(f'Muy poca luz. Busca mejor iluminación. (Brillo: {brightness_val:.1f})',
                                           'dark')
                elif brightness_val > self.MAX_BRIGHTNESS:
                    await self.send_status(f'Demasiada luz. Reduce la iluminación. (Brillo: {brightness_val:.1f})',
                                           'bright')
                else:
                    await self.send_status(f'Bajo contraste. Mejora la iluminación. (Contraste: {contrast_val:.1f})',
                                           'low_contrast')
                return

            await self.send_status(f'Buena calidad detectada. Score: {quality_score:.1f}', 'good_quality')

            if quality_score > self.best_score or self.frame_count >= self.max_frames_to_analyze:
                self.best_score = quality_score
                self.best_frame = face_roi

                await self.send_status(f'Mejor imagen encontrada. Score: {quality_score:.1f}', 'analyzing')

                if self.frame_count >= self.max_frames_to_analyze:
                    await self.save_best_frame()

        except Exception as e:
            await self.send_status('Error interno', 'error')

    async def save_best_frame(self):
        if self.best_frame is None:
            await self.send_status('No se encontró imagen de calidad suficiente', 'no_good_frame')
            return

        try:
            face_resized = cv2.resize(self.best_frame, (150, 200))
            face_bgr = cv2.cvtColor(face_resized, cv2.COLOR_RGB2BGR)

            _, face_bytes = cv2.imencode('.jpg', face_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
            face_image_bytes = face_bytes.tobytes()

            success = await self.save_facial_data(face_image_bytes)

            if success:
                self.face_registered = True
                await self.send_status(f'¡Rostro registrado exitosamente! (Score final: {self.best_score:.1f})',
                                       'success')
            else:
                await self.send_status('Error guardando datos', 'save_error')

        except Exception as e:
            logger.error(f"Error guardando mejor frame: {str(e)}")
            await self.send_status('Error procesando imagen final', 'error')

    @database_sync_to_async
    def save_facial_data(self, image_bytes):
        try:
            user = User.objects.get(id=self.user_id)
            facial_data, created = FacialData.objects.get_or_create(user=user)

            image_file = ContentFile(image_bytes, name=f'facial_{user.id}.jpg')
            facial_data.face_image = image_file
            facial_data.is_active = True
            facial_data.save()

            return True

        except Exception as e:
            logger.error(f"Error guardando: {str(e)}")
            return False

    async def send_status(self, message, status):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': message,
            'status': status,
            'registered': self.face_registered,
            'frames_analyzed': self.frame_count,
            'best_score': self.best_score
        }))

    async def receive_json_content(self, content):
        if content.get('action') == 'reset':
            self.face_registered = False
            self.best_frame = None
            self.best_score = 0
            self.frame_count = 0
            await self.send_status('Listo para nuevo registro', 'ready')
