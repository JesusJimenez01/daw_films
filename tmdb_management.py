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
        if params is None:
            params = {}

        params['api_key'] = cls.get_api_key()

        if 'language' not in params:
            params['language'] = 'es-ES'

        url = f"{cls.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar petición a TMDB: {e}")
            return {}


class MovieRequests(TMDBApi):
    """
    Clase específica para películas
    """

    @classmethod
    def get_popular_movies(cls, page=1, allow_adult=False):
        """
        Obtiene una lista de películas populares, filtrando si es necesario
        """
        data = cls.make_request('movie/popular', {'page': page})
        results = data.get('results', [])

        # Filtrar contenido adulto si no está permitido
        if not allow_adult:
            results = [movie for movie in results if not movie.get('adult', False)]

        data['results'] = results
        return data

    @classmethod
    def search_movies(cls, query, page=1, allow_adult=False):
        """
        Busca películas por término de búsqueda, incluye o excluye contenido adulto
        """
        data = cls.make_request(
            'search/movie',
            {'query': query, 'page': page, 'include_adult': allow_adult}
        )
        results = data.get('results', [])

        # Filtrar adicionalmente por si acaso la API devuelve adultos de todos modos
        if not allow_adult:
            results = [movie for movie in results if not movie.get('adult', False)]

        data['results'] = results
        return data

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
    def get_movie_recommendations(cls, movie_id, allow_adult=False):
        """Obtiene recomendaciones basadas en una película"""
        data = cls.make_request(f'movie/{movie_id}/recommendations')
        results = data.get('results', [])

        if not allow_adult:
            results = [movie for movie in results if not movie.get('adult', False)]

        data['results'] = results
        return data
