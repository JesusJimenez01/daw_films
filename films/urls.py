from django.urls import path
from .views import MovieListView, MovieDetailView
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
]