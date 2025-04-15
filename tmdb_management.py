import requests
from django.conf import settings


class TMDBApi:
    """
    Clase para interactuar con la API de TMDB
    """
    BASE_URL = 'https://api.themoviedb.org/3'

    @staticmethod
    def get_api_key():
        """Obtiene la clave API desde la configuración de Django"""
        return settings.TMDB_API_KEY

    @classmethod
    def make_request(cls, endpoint, params=None):
        """
        Método para realizar peticiones a la API de TMDB

        Args:
            endpoint (str): Endpoint de la API (por ejemplo 'movie/popular')
            params (dict): Parámetros adicionales para la consulta

        Returns:
            dict: Respuesta JSON de la API
        """
        # Preparar parámetros base
        if params is None:
            params = {}

        params['api_key'] = cls.get_api_key()

        if 'language' not in params:
            params['language'] = 'es-ES'

        url = f"{cls.BASE_URL}/{endpoint}"

        # Hacer la petición
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lanzar error para códigos de estado HTTP 4XX/5XX
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar petición a TMDB: {e}")
            return {}


class MovieRequests(TMDBApi):
    """
    Clase específica para películas
    """

    @classmethod
    def get_popular_movies(cls, page=1):
        """Obtiene una lista de películas populares"""
        return cls.make_request('movie/popular', {'page': page})

    @classmethod
    def search_movies(cls, query, page=1):
        """Busca películas por un término de búsqueda"""
        return cls.make_request('search/movie', {'query': query, 'page': page})

    @classmethod
    def get_movie_details(cls, movie_id):
        """Obtiene los detalles de una película específica"""
        return cls.make_request(f'movie/{movie_id}')

    @classmethod
    def get_movie_credits(cls, movie_id):
        """Obtiene los créditos (reparto y equipo) de una película"""
        return cls.make_request(f'movie/{movie_id}/credits')

    @classmethod
    def get_movie_videos(cls, movie_id):
        """Obtiene los videos relacionados con una película"""
        return cls.make_request(f'movie/{movie_id}/videos')

    @classmethod
    def get_movie_recommendations(cls, movie_id):
        """Obtiene películas recomendadas basadas en una película"""
        return cls.make_request(f'movie/{movie_id}/recommendations')