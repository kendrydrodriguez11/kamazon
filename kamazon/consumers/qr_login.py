from django.contrib.sessions.backends.db import SessionStore
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class QRLoginConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.room_group_name = None

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'{self.token}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected to group: {self.token}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.token, self.channel_name)
        print(f"WebSocket disconnected from group: {self.token}")

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def create_session(self, user):
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
        session.save()
        return session.session_key

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'user_id':
            user_id = text_data_json['user_id']
            user = await self.get_user(user_id)
            if user:
                session_key = await self.create_session(user)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_session_key',
                        'session_key': session_key
                    }
                )

        elif message_type == 'authenticated':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_authentication',
                    'message': 'authenticated'
                }
            )

    async def send_session_key(self, event):
        session_key = event['session_key']

        await self.send(text_data=json.dumps({
            'type': 'successful',
            'session_key': session_key
        }))

    async def send_authentication(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'authenticated',
            'message': message
        }))
