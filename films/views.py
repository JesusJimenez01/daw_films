from django.views.generic import ListView, DetailView
from django.http import Http404
from tmdb_management import MovieRequests


class MovieListView(ListView):
    """
    Vista para mostrar la lista de películas populares o resultados de búsqueda
    """
    template_name = 'films/index.html'
    context_object_name = 'movies'

    def get_queryset(self):
        """
        Obtiene las películas desde la API
        """
        search_query = self.request.GET.get('search', '')
        page_number = self.request.GET.get('page', 1)

        # Obtener películas (búsqueda o populares)
        if search_query:
            data = MovieRequests.search_movies(search_query, page_number)
        else:
            data = MovieRequests.get_popular_movies(page_number)

        # Obtener lista de películas o lista vacía si hay error
        movies = data.get('results', [])

        # Preparar datos adicionales para cada película
        for movie in movies:
            movie['rating_out_of_five'] = round(movie.get('vote_average', 0) / 2, 1)

        return movies

    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional para la plantilla
        """
        context = super().get_context_data(**kwargs)

        # Obtener datos para paginación
        search_query = self.request.GET.get('search', '')
        page_number = int(self.request.GET.get('page', 1))

        # Obtener datos completos para referencia
        if search_query:
            data = MovieRequests.search_movies(search_query, page_number)
        else:
            data = MovieRequests.get_popular_movies(page_number)

        # Información de paginación
        total_pages = data.get('total_pages', 1)
        page_range = range(max(1, page_number - 2), min(total_pages, page_number + 3))

        # Actualizar contexto
        context.update({
            'search_query': search_query,
            'current_page': page_number,
            'total_pages': total_pages,
            'page_range': page_range,
        })

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
        """
        Agrega información adicional al contexto
        """
        context = super().get_context_data(**kwargs)

        movie_id = self.kwargs.get('movie_id')

        # Obtener créditos (reparto y equipo)
        credits = MovieRequests.get_movie_credits(movie_id)
        top_cast = credits.get('cast', [])[:6]

        # Obtener videos (tráilers, etc.)
        videos = MovieRequests.get_movie_videos(movie_id)
        trailers = [v for v in videos.get('results', [])
                    if v.get('site') == 'YouTube' and v.get('type') == 'Trailer']

        # Obtener películas recomendadas
        recommendations = MovieRequests.get_movie_recommendations(movie_id)
        recommended_movies = recommendations.get('results', [])[:4]

        # Preparar datos adicionales
        for movie in recommended_movies:
            movie['rating_out_of_five'] = round(movie.get('vote_average', 0) / 2, 1)

        # Actualizar contexto
        context.update({
            'cast': top_cast,
            'trailers': trailers,
            'recommended_movies': recommended_movies
        })

        return context


