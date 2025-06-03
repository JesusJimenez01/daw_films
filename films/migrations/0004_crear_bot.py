from django.db import migrations
from django.contrib.auth.hashers import make_password

def crear_usuario_bot(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('films', 'Profile')        # Profile en films
    Friendship = apps.get_model('chat', 'Friendship')   # Friendship en chat

    # Crear usuario bot si no existe
    if not User.objects.filter(username='moviebot').exists():
        bot_user = User.objects.create(
            username='moviebot',
            password=make_password('bot1234'),
            first_name='Movie',
            last_name='Bot',
            is_active=True,
        )
        # Crear perfil del bot
        Profile.objects.create(user=bot_user, bio="Soy tu ayudante para encontrar películas 🎬", preferred_language='es')
    else:
        bot_user = User.objects.get(username='moviebot')

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        ('films', '0003_alter_movierating_options_movierating_poster_path_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_usuario_bot),
    ]
