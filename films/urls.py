from django.urls import path

from . import views
from .views import MovieListView, MovieDetailView, FavoritesListView, WatchlistView, UserReviewsView
from .auth_views import LoginView, RegisterView, ProfileView, logout_view

urlpatterns = [
    # Páginas principales
    path('', MovieListView.as_view(), name='index'),
    path('movie/<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),

    # Autenticación y perfil
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', logout_view, name='logout'),

    # Funcionalidades de usuarios
    path('favorites/add/<int:movie_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:movie_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('movie/<int:movie_id>/add_review/', views.add_review, name='add_review'),
    path('movie/<int:movie_id>/edit_review/', views.edit_review, name='edit_review'),
    path('favorites/', FavoritesListView.as_view(), name='favorites'),
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('reviews/', UserReviewsView.as_view(), name='user_reviews'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),

]
