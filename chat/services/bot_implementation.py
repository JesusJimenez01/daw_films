import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Message


class RasaBotImplement:
    """
    Integrar Rasa con Django
    """

    def __init__(self):
        # URL de server Rasa (según endpoints.yml)
        self.rasa_url = getattr(settings, 'RASA_URL', 'http://localhost:5005')
        self.bot_username = getattr(settings, 'BOT_USERNAME', 'moviebot')

    def get_bot_user(self):
        """Obtiene el usuario bot"""
        try:
            return User.objects.get(username=self.bot_username)
        except User.DoesNotExist:
            return None

    def send_message_to_rasa(self, message, sender_id):
        """
        Envía un mensaje a Rasa y obtiene la respuesta
        """
        try:
            payload = {
                "sender": sender_id,
                "message": message
            }

            response = requests.post(
                f"{self.rasa_url}/webhooks/rest/webhook",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                bot_responses = response.json()
                return bot_responses
            else:
                return [{"text": "Lo siento, tengo problemas técnicos. Intenta más tarde."}]

        except requests.exceptions.RequestException:
            return [{"text": "No puedo conectar con el servidor. Intenta más tarde."}]

    def process_user_message(self, user_message, sender_user):
        """
        Procesa un mensaje del usuario y genera respuesta del bot
        """
        bot_user = self.get_bot_user()
        if not bot_user:
            return None

        # Enviar mensaje a Rasa
        sender_id = f"user_{sender_user.id}"
        bot_responses = self.send_message_to_rasa(user_message.content, sender_id)

        # Crear mensajes de respuesta del bot
        bot_messages = []
        for response in bot_responses:
            if 'text' in response:
                bot_message = Message.objects.create(
                    sender=bot_user,
                    receiver=sender_user,
                    content=response['text'],
                    timestamp=timezone.now()
                )
                bot_messages.append(bot_message)

        return bot_messages