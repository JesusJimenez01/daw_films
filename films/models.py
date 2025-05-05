from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Modelo para el perfil de usuario extendido
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profile_avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    favorite_genres = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    # Preferencias
    preferred_language = models.CharField(max_length=10, default='es')
    show_adult_content = models.BooleanField(default=False)

    # Campos para listas personalizadas (relaciones añadidas abajo)

    def __str__(self):
        return f'{self.user.username} Profile'


class WatchlistItem(models.Model):
    """
    Modelo para películas en la lista de seguimiento del usuario
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watchlist')
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie_id')
        ordering = ['-added_date']

    def __str__(self):
        return f'{self.title} - Watchlist de {self.profile.user.username}'


class FavoriteMovie(models.Model):
    """
    Modelo para películas favoritas del usuario
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='favorites')
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie_id')
        ordering = ['-added_date']

    def __str__(self):
        return f'{self.title} - Favorito de {self.profile.user.username}'


class MovieRating(models.Model):
    """
    Modelo para las valoraciones de películas por usuarios
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ratings')
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1)  # Valoración de 0.5 a 5.0
    comment = models.TextField(blank=True)
    date_rated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'movie_id')
        ordering = ['-date_rated']

    def __str__(self):
        return f'{self.title} - {self.rating}/5 por {self.profile.user.username}'
