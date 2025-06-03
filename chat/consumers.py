# Consumidor de WebSocket para el chat

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Friendship
from django.utils import timezone
from .services.bot_implementation import RasaBotImplement


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.bot_service = RasaBotImplement()

        # Verifica si el usuario está autenticado
        if not self.user.is_authenticated:
            await self.close()
            return

        # Verifica si el otro usuario existe
        try:
            self.other_user = await database_sync_to_async(User.objects.get)(username=self.other_username)
        except User.DoesNotExist:
            await self.close()
            return

        # Verificar que sean amigos
        if not await self.are_friends(self.user, self.other_user):
            await self.close()
            return

        # Crea un nombre de grupo único para esta conversación
        users = sorted([self.user.username, self.other_user.username])
        self.room_group_name = f'chat_{users[0]}_{users[1]}'

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Enviar confirmación de conexión
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado al chat'
        }))

    async def disconnect(self, close_code):
        # Salir del grupo al desconectar
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')

            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato de mensaje inválido'
            }))

    async def handle_chat_message(self, data):
        message = data.get('message', '').strip()
        if not message:
            return

        # Guardar mensaje en la base de datos
        db_message = await self.save_message(message)

        # Obtener URL del avatar del remitente
        avatar_url = await self.get_user_avatar(self.user)

        # Enviar mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'timestamp': db_message.timestamp.isoformat(),
                'avatar_url': avatar_url,
                'message_id': db_message.id
            }
        )

        # Si el receptor es el bot, generar respuesta automática
        if self.other_username == 'moviebot':
            await self.handle_bot_response(db_message)

    async def handle_bot_response(self, user_message):
        """
        Maneja la respuesta automática del bot usando Rasa
        """
        try:
            # Procesar mensaje con Rasa (ejecutar en hilo separado)
            bot_messages = await database_sync_to_async(
                self.bot_service.process_user_message
            )(user_message, self.user)

            if bot_messages:
                # Enviar cada respuesta del bot
                for bot_message in bot_messages:
                    avatar_url = await self.get_user_avatar(bot_message.sender)

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': bot_message.content,
                            'username': bot_message.sender.username,
                            'timestamp': bot_message.timestamp.isoformat(),
                            'avatar_url': avatar_url,
                            'message_id': bot_message.id
                        }
                    )

        except Exception:
            # Si hay error, no hacer nada - el usuario verá que el bot no responde
            pass

    async def handle_typing(self, data):
        is_typing = data.get('typing', False)

        # No mostrar "escribiendo" si es el bot
        if self.other_username != 'moviebot':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'typing': is_typing,
                    'username': self.user.username
                }
            )

    async def chat_message(self, event):
        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'avatar_url': event.get('avatar_url', ''),
            'message_id': event.get('message_id')
        }))

    async def typing_status(self, event):
        # Solo enviar el estado de escritura si no es del usuario actual
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'typing': event['typing'],
                'username': event['username']
            }))

    @database_sync_to_async
    def save_message(self, content):
        # Guardar mensaje en la base de datos
        return Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            content=content,
            timestamp=timezone.now()
        )

    @database_sync_to_async
    def are_friends(self, user1, user2):
        # Verificar si los usuarios son amigos
        return Friendship.are_friends(user1, user2)

    @database_sync_to_async
    def get_user_avatar(self, user):
        # Obtener URL del avatar del usuario
        try:
            if hasattr(user, 'profile') and user.profile.avatar:
                return user.profile.avatar.url
        except:
            pass
        return None