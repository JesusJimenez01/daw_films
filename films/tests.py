from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from unittest.mock import patch
from films.models import FavoriteMovie, MovieRating, WatchlistItem
from films.models import Profile


class BaseTestCase(TestCase):
    """
    Clase base con configuración común para todos los tests
    """

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()

        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Asegurar que existe el perfil
        self.profile, created = Profile.objects.get_or_create(user=self.user)

        # Datos de película de prueba
        self.movie_data = {
            'id': 123,
            'title': 'Test Movie',
            'poster_path': '/test_poster.jpg',
            'vote_average': 8.5,
            'overview': 'Test movie overview',
            'release_date': '2023-01-01'
        }

        # Mock de respuesta de API exitosa
        self.api_success_response = {
            'results': [self.movie_data],
            'total_pages': 1,
            'page': 1
        }


class MovieListViewTest(BaseTestCase):
    """Tests para la vista de lista de películas"""

    @patch('films.views.MovieRequests.get_popular_movies')
    def test_movie_list_view_get_popular_movies(self, mock_get_popular):
        """Test que verifica la obtención de películas populares"""
        mock_get_popular.return_value = self.api_success_response

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Movie')
        mock_get_popular.assert_called_once_with(1, allow_adult=False)

    @patch('films.views.MovieRequests.search_movies')
    def test_movie_list_view_search_movies(self, mock_search):
        """Test que verifica la búsqueda de películas"""
        mock_search.return_value = self.api_success_response

        response = self.client.get(reverse('index'), {'search': 'test query'})

        self.assertEqual(response.status_code, 200)
        mock_search.assert_called_once_with('test query', 1, allow_adult=False)

    def test_movie_list_view_rating_calculation(self):
        """Test que verifica el cálculo de rating de 5 estrellas"""
        with patch('films.views.MovieRequests.get_popular_movies') as mock_get_popular:
            mock_get_popular.return_value = self.api_success_response

            response = self.client.get(reverse('index'))
            movies = response.context['movies']

            # Verificar que el rating se calcula correctamente (8.5/2 = 4.25 -> 4.3)
            expected_rating = round(8.5 / 2, 1)
            self.assertEqual(movies[0]['rating_out_of_five'], expected_rating)

    def test_movie_list_view_authenticated_user_context(self):
        """Test del contexto para usuarios autenticados"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear datos de prueba
        FavoriteMovie.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie'
        )

        with patch('films.views.MovieRequests.get_popular_movies') as mock_get_popular:
            mock_get_popular.return_value = self.api_success_response

            response = self.client.get(reverse('index'))

            self.assertIn('favorite_ids', response.context)
            self.assertIn('watchlist_ids', response.context)
            self.assertIn(123, response.context['favorite_ids'])


class MovieDetailViewTest(BaseTestCase):
    """Tests para la vista de detalle de película"""

    @patch('films.views.MovieRequests.get_movie_details')
    @patch('films.views.MovieRequests.get_movie_credits')
    @patch('films.views.MovieRequests.get_movie_videos')
    @patch('films.views.MovieRequests.get_movie_recommendations')
    def test_movie_detail_view_success(self, mock_recommendations, mock_videos,
                                       mock_credits, mock_details):
        """Test de vista de detalle exitosa"""
        # Configurar mocks
        mock_details.return_value = self.movie_data
        mock_credits.return_value = {'cast': [{'name': 'Actor Test'}]}
        mock_videos.return_value = {'results': []}
        mock_recommendations.return_value = {'results': []}

        response = self.client.get(reverse('movie_detail', kwargs={'movie_id': 123}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['movie']['title'], 'Test Movie')

    @patch('films.views.MovieRequests.get_movie_details')
    def test_movie_detail_view_not_found(self, mock_details):
        """Test de película no encontrada"""
        mock_details.return_value = {'success': False}

        response = self.client.get(reverse('movie_detail', kwargs={'movie_id': 999}))

        self.assertEqual(response.status_code, 404)

    def test_movie_detail_view_with_user_review(self):
        """Test de detalle con reseña del usuario"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear reseña de prueba
        MovieRating.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie',
            rating=5,
            comment='Great movie!'
        )

        with patch('films.views.MovieRequests.get_movie_details') as mock_details:
            mock_details.return_value = self.movie_data
            with patch('films.views.MovieRequests.get_movie_credits') as mock_credits:
                mock_credits.return_value = {'cast': []}
                with patch('films.views.MovieRequests.get_movie_videos') as mock_videos:
                    mock_videos.return_value = {'results': []}
                    with patch('films.views.MovieRequests.get_movie_recommendations') as mock_recommendations:
                        mock_recommendations.return_value = {'results': []}

                        response = self.client.get(reverse('movie_detail', kwargs={'movie_id': 123}))

                        self.assertIsNotNone(response.context['user_review'])
                        self.assertEqual(response.context['user_review'].rating, 5)


class FavoritesViewTest(BaseTestCase):
    """Tests para la vista de favoritos"""

    def test_favorites_view_requires_login(self):
        """Test que verifica que se requiere login"""
        response = self.client.get(reverse('favorites'))
        self.assertRedirects(response, '/login/?next=/favorites/')

    def test_favorites_view_authenticated_user(self):
        """Test de vista de favoritos para usuario autenticado"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear favorito de prueba
        FavoriteMovie.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie',
            poster_path='/test.jpg'
        )

        response = self.client.get(reverse('favorites'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['favorites']), 1)
        self.assertEqual(response.context['favorites'][0].title, 'Test Movie')


class AddToFavoritesTest(BaseTestCase):
    """Tests para añadir películas a favoritos"""

    @patch('films.views.MovieRequests.get_movie_details')
    def test_add_to_favorites_success(self, mock_details):
        """Test de añadir a favoritos exitosamente"""
        mock_details.return_value = self.movie_data
        self.client.login(username='testuser', password='testpassword123')

        response = self.client.post(reverse('add_to_favorites', kwargs={'movie_id': 123}))

        self.assertTrue(FavoriteMovie.objects.filter(
            profile=self.profile, movie_id=123
        ).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('añadida a tus favoritos' in str(m) for m in messages))

    @patch('films.views.MovieRequests.get_movie_details')
    def test_add_to_favorites_already_exists(self, mock_details):
        """Test de añadir película que ya está en favoritos"""
        mock_details.return_value = self.movie_data
        self.client.login(username='testuser', password='testpassword123')

        # Crear favorito existente
        FavoriteMovie.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie'
        )

        response = self.client.post(reverse('add_to_favorites', kwargs={'movie_id': 123}))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('ya está en tus favoritos' in str(m) for m in messages))

    def test_add_to_favorites_requires_login(self):
        """Test que verifica que se requiere login"""
        response = self.client.post(reverse('add_to_favorites', kwargs={'movie_id': 123}))
        self.assertRedirects(response, '/login/?next=/favorites/add/123/')


class RemoveFromFavoritesTest(BaseTestCase):
    """Tests para eliminar de favoritos"""

    def test_remove_from_favorites_success(self):
        """Test de eliminación exitosa de favoritos"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear favorito para eliminar
        favorite = FavoriteMovie.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie'
        )

        response = self.client.post(reverse('remove_from_favorites', kwargs={'movie_id': 123}))

        self.assertFalse(FavoriteMovie.objects.filter(id=favorite.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('eliminada de tus favoritos' in str(m) for m in messages))

    def test_remove_from_favorites_not_found(self):
        """Test de eliminación de favorito inexistente"""
        self.client.login(username='testuser', password='testpassword123')

        response = self.client.post(reverse('remove_from_favorites', kwargs={'movie_id': 999}))
        self.assertEqual(response.status_code, 404)


class ReviewViewsTest(BaseTestCase):
    """Tests para las vistas de reseñas"""

    @patch('films.views.MovieRequests.get_movie_details')
    def test_add_review_success(self, mock_details):
        """Test de añadir reseña exitosamente"""
        mock_details.return_value = self.movie_data
        self.client.login(username='testuser', password='testpassword123')

        response = self.client.post(reverse('add_review', kwargs={'movie_id': 123}), {
            'rating': 5,
            'comment': 'Excellent movie!'
        })

        self.assertTrue(MovieRating.objects.filter(
            profile=self.profile, movie_id=123
        ).exists())

        review = MovieRating.objects.get(profile=self.profile, movie_id=123)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent movie!')

    def test_edit_review_success(self):
        """Test de edición de reseña exitosa"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear reseña existente
        review = MovieRating.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie',
            rating=3,
            comment='Original comment'
        )

        response = self.client.post(reverse('edit_review', kwargs={'movie_id': 123}), {
            'rating': 5,
            'comment': 'Updated comment'
        })

        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Updated comment')

    def test_delete_review_success(self):
        """Test de eliminación de reseña exitosa"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear reseña para eliminar
        review = MovieRating.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie',
            rating=4,
            comment='Test comment'
        )

        response = self.client.post(reverse('delete_review', kwargs={'review_id': review.id}))

        self.assertFalse(MovieRating.objects.filter(id=review.id).exists())

    def test_user_reviews_view(self):
        """Test de vista de reseñas del usuario"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear reseñas de prueba
        MovieRating.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie 1',
            rating=5,
            comment='Great!'
        )

        MovieRating.objects.create(
            profile=self.profile,
            movie_id=124,
            title='Test Movie 2',
            rating=3,
            comment='Okay'
        )

        response = self.client.get(reverse('user_reviews'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['reviews']), 2)


class WatchlistViewsTest(BaseTestCase):
    """Tests para las vistas de watchlist"""

    @patch('films.views.MovieRequests.get_movie_details')
    def test_add_to_watchlist_success(self, mock_details):
        """Test de añadir a watchlist exitosamente"""
        mock_details.return_value = self.movie_data
        self.client.login(username='testuser', password='testpassword123')

        response = self.client.post(reverse('add_to_watchlist', kwargs={'movie_id': 123}))

        self.assertTrue(WatchlistItem.objects.filter(
            profile=self.profile, movie_id=123
        ).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('añadida a tu watchlist' in str(m) for m in messages))

    def test_remove_from_watchlist_success(self):
        """Test de eliminación de watchlist exitosa"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear item de watchlist para eliminar
        watchlist_item = WatchlistItem.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie'
        )

        response = self.client.post(reverse('remove_from_watchlist', kwargs={'movie_id': 123}))

        self.assertFalse(WatchlistItem.objects.filter(id=watchlist_item.id).exists())

    def test_watchlist_view(self):
        """Test de vista de watchlist"""
        self.client.login(username='testuser', password='testpassword123')

        # Crear items de watchlist de prueba
        WatchlistItem.objects.create(
            profile=self.profile,
            movie_id=123,
            title='Test Movie 1'
        )

        WatchlistItem.objects.create(
            profile=self.profile,
            movie_id=124,
            title='Test Movie 2'
        )

        response = self.client.get(reverse('watchlist'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['watchlist_items']), 2)


class ErrorHandlingTest(BaseTestCase):
    """Tests para manejo de errores"""

    @patch('films.views.MovieRequests.get_movie_details')
    def test_add_to_favorites_movie_not_found(self, mock_details):
        """Test de manejo de error cuando no se encuentra la película"""
        mock_details.return_value = {'success': False}
        self.client.login(username='testuser', password='testpassword123')

        response = self.client.post(reverse('add_to_favorites', kwargs={'movie_id': 999}))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('No se pudo encontrar' in str(m) for m in messages))

    @patch('films.views.MovieRequests.get_popular_movies')
    def test_movie_list_view_api_error(self, mock_get_popular):
        """Test de manejo de error en la API"""
        mock_get_popular.return_value = {}  # Respuesta vacía simula error

        response = self.client.get(reverse('index'))

        # Debe devolver una lista vacía cuando hay error
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['movies']), 0)


class PaginationTest(BaseTestCase):
    """Tests para paginación"""

    @patch('films.views.MovieRequests.get_popular_movies')
    def test_pagination_context(self, mock_get_popular):
        """Test del contexto de paginación"""
        mock_response = {
            'results': [self.movie_data],
            'total_pages': 10,
            'page': 3
        }
        mock_get_popular.return_value = mock_response

        response = self.client.get(reverse('index'), {'page': 3})

        self.assertEqual(response.context['current_page'], 3)
        self.assertEqual(response.context['total_pages'], 10)
        self.assertIn('page_range', response.context)


class AdultContentFilterTest(BaseTestCase):
    """Tests para filtrado de contenido adulto"""

    @patch('films.views.MovieRequests.get_popular_movies')
    def test_adult_content_filter_authenticated_user(self, mock_get_popular):
        """Test de filtro de contenido adulto para usuario autenticado"""
        self.client.login(username='testuser', password='testpassword123')

        # Configurar preferencias del usuario
        self.profile.show_adult_content = False
        self.profile.save()

        mock_get_popular.return_value = self.api_success_response

        response = self.client.get(reverse('index'))

        # Verificar que se llamó con allow_adult=False
        mock_get_popular.assert_called_with(1, allow_adult=False)

    @patch('films.views.MovieRequests.get_popular_movies')
    def test_adult_content_filter_anonymous_user(self, mock_get_popular):
        """Test de filtro de contenido adulto para usuario anónimo"""
        mock_get_popular.return_value = self.api_success_response

        response = self.client.get(reverse('index'))

        mock_get_popular.assert_called_with(1, allow_adult=False)