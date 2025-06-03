from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

from chat.models import Friendship
from .models import Profile
from django.contrib.auth.models import User


# Señal para crear perfil automáticamente al crear un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_friendship_with_bot(sender, instance, created, **kwargs):
    if created and instance.username != 'moviebot':  # Evitar que el bot se haga amigo de sí mismo
        try:
            bot_user = User.objects.get(username='moviebot')
        except User.DoesNotExist:
            return

        # Crear una relación de amistad (bot como solicitante)
        if not Friendship.objects.filter(
                models.Q(requester=bot_user, receiver=instance) |
                models.Q(requester=instance, receiver=bot_user)
        ).exists():
            Friendship.objects.create(requester=bot_user, receiver=instance, is_accepted=True)
