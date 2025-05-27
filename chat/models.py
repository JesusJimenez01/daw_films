from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Friendship(models.Model):
    """
    Modelo para gestionar las relaciones de amistad entre usuarios
    """
    requester = models.ForeignKey(User, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='friendship_requests_received', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('requester', 'receiver')
        verbose_name = 'Amistad'
        verbose_name_plural = 'Amistades'

    def __str__(self):
        status = 'aceptada' if self.is_accepted else 'pendiente'
        return f'Solicitud de {self.requester.username} a {self.receiver.username} ({status})'

    @property
    def is_mutual(self):
        return self.is_accepted

    @classmethod
    def get_friends(cls, user):
        """
        Devuelve todos los amigos aceptados de un usuario
        """
        # Amistades donde el usuario es el solicitante y han sido aceptadas
        friends_as_requester = cls.objects.filter(
            requester=user,
            is_accepted=True
        ).select_related('receiver__profile')

        # Amistades donde el usuario es el receptor y han sido aceptadas
        friends_as_receiver = cls.objects.filter(
            receiver=user,
            is_accepted=True
        ).select_related('requester__profile')

        # Combinar los dos conjuntos de amigos
        friends = []
        for friendship in friends_as_requester:
            friends.append(friendship.receiver)

        for friendship in friends_as_receiver:
            friends.append(friendship.requester)

        return friends

    @classmethod
    def get_pending_requests(cls, user):
        """
        Devuelve las solicitudes de amistad pendientes recibidas por el usuario
        """
        return cls.objects.filter(
            receiver=user,
            is_accepted=False
        ).select_related('requester__profile')

    @classmethod
    def are_friends(cls, user1, user2):
        """
        Comprueba si dos usuarios son amigos
        """
        friendship1 = cls.objects.filter(requester=user1, receiver=user2, is_accepted=True).exists()
        friendship2 = cls.objects.filter(requester=user2, receiver=user1, is_accepted=True).exists()
        return friendship1 or friendship2


class Message(models.Model):
    """
    Modelo para los mensajes entre amigos
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'

    def __str__(self):
        return f'Mensaje de {self.sender.username} a {self.receiver.username}'

    @classmethod
    def get_conversations(cls, user):
        """
        Devuelve todas las conversaciones del usuario agrupadas por amigo
        """
        # Obtener mensajes enviados y recibidos por el usuario
        sent_messages = cls.objects.filter(sender=user).select_related('receiver')
        received_messages = cls.objects.filter(receiver=user).select_related('sender')

        # Recopilar usuarios únicos con los que ha habido conversación
        conversation_partners = set()

        for message in sent_messages:
            conversation_partners.add(message.receiver)

        for message in received_messages:
            conversation_partners.add(message.sender)

        return conversation_partners

    @classmethod
    def get_conversation(cls, user1, user2):
        """
        Devuelve la conversación entre dos usuarios
        """
        messages = cls.objects.filter(
            (models.Q(sender=user1, receiver=user2) |
             models.Q(sender=user2, receiver=user1))
        ).order_by('timestamp')

        # Marcar como leídos los mensajes recibidos
        unread_messages = messages.filter(receiver=user1, is_read=False)
        unread_messages.update(is_read=True)

        return messages

    @classmethod
    def get_unread_count(cls, user):
        """
        Devuelve el número de mensajes no leídos por usuario
        """
        return cls.objects.filter(receiver=user, is_read=False).count()

    @classmethod
    def get_unread_by_sender(cls, receiver, sender):
        """
        Devuelve el número de mensajes no leídos de un remitente específico
        """
        return cls.objects.filter(
            receiver=receiver,
            sender=sender,
            is_read=False
        ).count()