from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.http import Http404

from films.models import FavoriteMovie, MovieRating, WatchlistItem
from tmdb_management import MovieRequests
from django.contrib import messages


class MovieListView(ListView):
    """
    Vista para mostrar la lista de películas populares o resultados de búsqueda
    """
    template_name = 'films/index.html'
    context_object_name = 'movies'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_data = None  # Cache para evitar llamadas duplicadas a la API

    def get_api_data(self):
        """
        Obtiene los datos de la API una sola vez y los cachea
        """
        if self._api_data is None:
            search_query = self.request.GET.get('search', '')
            page_number = int(self.request.GET.get('page', 1))

            # Obtener la preferencia de contenido adulto del usuario
            allow_adult = False  # Por defecto False para usuarios anónimos
            if self.request.user.is_authenticated:
                allow_adult = self.request.user.profile.show_adult_content

            # Obtener películas (búsqueda o populares) con filtrado de contenido adulto
            if search_query:
                self._api_data = MovieRequests.search_movies(search_query, page_number, allow_adult=allow_adult)
            else:
                self._api_data = MovieRequests.get_popular_movies(page_number, allow_adult=allow_adult)

        return self._api_data or {}

    def get_queryset(self):
        """
        Obtiene las películas desde la API
        """
        data = self.get_api_data()

        # Obtener lista de películas o lista vacía si hay error
        movies = data.get('results', [])

        # Preparar datos adicionales para cada película
        for movie in movies:
            movie['rating_out_of_five'] = round(movie.get('vote_average', 0) / 2, 1)

        return movies

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('search', '')
        page_number = int(self.request.GET.get('page', 1))

        # Usar los datos cacheados en lugar de hacer otra llamada a la API
        data = self.get_api_data()

        total_pages = data.get('total_pages', 1)
        page_range = range(max(1, page_number - 2), min(total_pages, page_number + 3))

        context.update({
            'search_query': search_query,
            'current_page': page_number,
            'total_pages': total_pages,
            'page_range': page_range,
        })

        # Añadir IDs de favoritos y watchlist al contexto
        if self.request.user.is_authenticated:
            favorite_ids = list(self.request.user.profile.favorites.values_list('movie_id', flat=True))
            watchlist_ids = list(
                WatchlistItem.objects.filter(profile=self.request.user.profile).values_list('movie_id', flat=True)
            )
            context['favorite_ids'] = favorite_ids
            context['watchlist_ids'] = watchlist_ids
        else:
            context['favorite_ids'] = []
            context['watchlist_ids'] = []

        return context


class MovieDetailView(DetailView):
    """
    Vista para mostrar los detalles de una película específica
    """
    template_name = 'films/movie_detail.html'
    context_object_name = 'movie'

    def get_object(self):
        """
        Obtiene el objeto película de la API en lugar de la base de datos
        """
        movie_id = self.kwargs.get('movie_id')
        movie = MovieRequests.get_movie_details(movie_id)

        # Comprobar si hay error en la respuesta de la API
        if movie.get('success', True) is False:
            raise Http404(f"Película con ID {movie_id} no encontrada")

        return movie

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs.get('movie_id')

        # Contenido adulto
        allow_adult = True
        if self.request.user.is_authenticated:
            allow_adult = self.request.user.profile.show_adult_content

        # Cast
        credits = MovieRequests.get_movie_credits(movie_id)
        top_cast = credits.get('cast', [])[:6]

        # Trailers
        videos = MovieRequests.get_movie_videos(movie_id)
        trailers = [v for v in videos.get('results', [])
                    if v.get('site') == 'YouTube' and v.get('type') == 'Trailer']

        # Recomendaciones
        recommendations = MovieRequests.get_movie_recommendations(movie_id, allow_adult=allow_adult)
        recommended_movies = recommendations.get('results', [])[:4]
        for movie in recommended_movies:
            movie['rating_out_of_five'] = round(movie.get('vote_average', 0) / 2, 1)

        # Reviews
        reviews = MovieRating.objects.filter(movie_id=movie_id).select_related('profile__user')

        user_review = None
        if self.request.user.is_authenticated:
            user_review = reviews.filter(profile=self.request.user.profile).first()

        context.update({
            'cast': top_cast,
            'trailers': trailers,
            'recommended_movies': recommended_movies,
            'reviews': reviews,
            'user_review': user_review,
        })

        if self.request.user.is_authenticated:
            favorite_ids = list(self.request.user.profile.favorites.values_list('movie_id', flat=True))
            watchlist_ids = list(
                WatchlistItem.objects.filter(profile=self.request.user.profile).values_list('movie_id', flat=True))
            context['favorite_ids'] = favorite_ids
            context['watchlist_ids'] = watchlist_ids
        else:
            context['favorite_ids'] = []
            context['watchlist_ids'] = []

        return context


@method_decorator(login_required, name='dispatch')
class FavoritesListView(ListView):
    """
    Vista para mostrar todas las películas favoritas del usuario
    """
    model = FavoriteMovie
    template_name = 'films/favorites.html'
    context_object_name = 'favorites'
    paginate_by = 12  # Número de favoritos por página

    def get_queryset(self):
        """
        Filtra los favoritos del usuario actual
        """
        return FavoriteMovie.objects.filter(profile=self.request.user.profile).order_by('-added_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Películas Favoritas'
        return context


@method_decorator(login_required, name='dispatch')
class WatchlistView(ListView):
    """
    Vista para mostrar la watchlist del usuario
    """
    model = WatchlistItem
    template_name = 'films/watchlist.html'
    context_object_name = 'watchlist_items'
    paginate_by = 12  # Número de items por página

    def get_queryset(self):
        """
        Filtra los elementos de la watchlist del usuario actual
        """
        return WatchlistItem.objects.filter(profile=self.request.user.profile).order_by('-added_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mi Lista de Películas por Ver'
        return context


@method_decorator(login_required, name='dispatch')
class UserReviewsView(ListView):
    """
    Vista para mostrar todas las reseñas del usuario
    """
    model = MovieRating
    template_name = 'films/user_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10  # Número de reseñas por página

    def get_queryset(self):
        """
        Filtra las reseñas del usuario actual
        """
        reviews = MovieRating.objects.filter(profile=self.request.user.profile).order_by('-date_rated')

        # Usar datos de la API para obtener los pósters
        for review in reviews:
            if not hasattr(review, 'poster_path') or not review.poster_path:
                # Obtener información de la película desde TMDB para conseguir el póster
                movie_details = MovieRequests.get_movie_details(review.movie_id)
                review.poster_path = movie_details.get('poster_path', '')

        return reviews

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Valoraciones de Películas'
        return context


@login_required
def add_to_favorites(request, movie_id):
    """
    Añade una película a los favoritos del usuario
    """
    # Obtener detalles de la película
    movie = MovieRequests.get_movie_details(movie_id)

    # Verificar si la película existe
    if movie.get('success', True) is False:
        messages.error(request, 'No se pudo encontrar la película solicitada')
        return redirect('index')

    # Crear o actualizar el elemento en favoritos
    favorite, created = FavoriteMovie.objects.get_or_create(
        profile=request.user.profile,
        movie_id=movie_id,
        defaults={
            'title': movie.get('title', ''),
            'poster_path': movie.get('poster_path')
        }
    )

    # Mensaje según la acción realizada
    if created:
        messages.success(request, f'"{movie.get("title")}" ha sido añadida a tus favoritos')
    else:
        messages.info(request, f'"{movie.get("title")}" ya está en tus favoritos')

    # Redirigir a la página anterior o a la de detalles de la película
    return redirect(request.META.get('HTTP_REFERER', f'/movie/{movie_id}/'))


@login_required
def remove_from_favorites(request, movie_id):
    """
    Elimina una película de los favoritos del usuario
    """
    # Intentar obtener y eliminar el elemento
    favorite = get_object_or_404(FavoriteMovie, profile=request.user.profile, movie_id=movie_id)
    title = favorite.title
    favorite.delete()

    messages.success(request, f'"{title}" ha sido eliminada de tus favoritos')

    # Redirigir a la página anterior o a la lista de favoritos
    return redirect(request.META.get('HTTP_REFERER', 'favorites'))


@login_required
def add_review(request, movie_id):
    """
    Añade una nueva reseña de película
    """
    # Obtener detalles de la película
    movie = MovieRequests.get_movie_details(movie_id)

    # Verificar si la película existe
    if movie.get('success', True) is False:
        messages.error(request, 'No se pudo encontrar la película solicitada')
        return redirect('index')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Crear la nueva reseña
        MovieRating.objects.create(
            profile=request.user.profile,
            movie_id=movie_id,
            title=movie.get('title', ''),
            poster_path=movie.get('poster_path', ''),
            rating=rating,
            comment=comment
        )

        messages.success(request, f'Tu reseña para "{movie.get("title")}" ha sido publicada')
        return redirect('movie_detail', movie_id=movie_id)

    # Si no es POST, redirigir a la página de detalles
    return redirect('movie_detail', movie_id=movie_id)


@login_required
def edit_review(request, movie_id):
    """
    Edita una reseña existente
    """
    # Obtener la reseña existente
    review = get_object_or_404(MovieRating, profile=request.user.profile, movie_id=movie_id)

    if request.method == 'POST':
        # Actualizar los campos
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()

        messages.success(request, 'Tu reseña ha sido actualizada')

    # Redirigir a la página de detalles
    return redirect('movie_detail', movie_id=movie_id)


@login_required
def delete_review(request, review_id):
    """
    Elimina una reseña existente
    """
    # Obtener la reseña y verificar que pertenece al usuario actual
    review = get_object_or_404(MovieRating, id=review_id, profile=request.user.profile)
    review.delete()

    # Redirigir a la página anterior o a la lista de reseñas
    return redirect(request.META.get('HTTP_REFERER', 'user_reviews'))


@login_required
def add_to_watchlist(request, movie_id):
    """
    Añade una película a la watchlist del usuario
    """
    # Obtener detalles de la película
    movie = MovieRequests.get_movie_details(movie_id)

    # Crear o actualizar el elemento en la watchlist
    watchlist_item, created = WatchlistItem.objects.get_or_create(
        profile=request.user.profile,
        movie_id=movie_id,
        defaults={
            'title': movie.get('title', ''),
            'poster_path': movie.get('poster_path')
        }
    )

    # Añadir mensaje según el resultado de la operación
    if created:
        messages.success(request, f'"{movie.get("title", "Película")}" ha sido añadida a tu watchlist')
    else:
        messages.info(request, f'"{movie.get("title", "Película")}" ya estaba en tu watchlist')

    # Redirigir a la página anterior
    return redirect(request.META.get('HTTP_REFERER', f'/movie/{movie_id}/'))


@login_required
def remove_from_watchlist(request, movie_id):
    """
    Elimina una película de la watchlist del usuario
    """
    # Intentar obtener y eliminar el elemento
    watchlist_item = get_object_or_404(WatchlistItem, profile=request.user.profile, movie_id=movie_id)
    watchlist_item.delete()

    # Redirigir a la página anterior
    return redirect(request.META.get('HTTP_REFERER', 'watchlist'))