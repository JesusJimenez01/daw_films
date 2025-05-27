from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string

from tmdb_management import MovieRequests
from .models import FavoriteMovie, WatchlistItem


@login_required
def add_to_favorites_partial(request, movie_id):
    """
    Añade una película a los favoritos del usuario y devuelve solo el fragmento del ícono actualizado.
    """
    movie = MovieRequests.get_movie_details(movie_id)

    if movie.get('success', True) is False:
        messages.error(request, 'No se pudo encontrar la película solicitada')
        return redirect('index')

    # Crear o actualizar el elemento en favoritos
    favorite, created = FavoriteMovie.objects.get_or_create(
        profile=request.user.profile,
        movie_id=movie_id,
        defaults={'title': movie.get('title', ''), 'poster_path': movie.get('poster_path')}
    )

    if created:
        messages.success(request, f'"{movie.get("title")}" ha sido añadida a tus favoritos')
    else:
        messages.info(request, f'"{movie.get("title")}" ya está en tus favoritos')

    # Devuelve solo el fragmento del ícono actualizado
    return HttpResponse(render_to_string('partials/favorite_icon.html', {'movie_id': movie_id, 'favorite': True}))


@login_required
def remove_from_favorites_partial(request, movie_id):
    """
    Elimina una película de los favoritos del usuario y devuelve solo el fragmento del ícono actualizado.
    """
    favorite = get_object_or_404(FavoriteMovie, profile=request.user.profile, movie_id=movie_id)
    title = favorite.title
    favorite.delete()

    messages.success(request, f'"{title}" ha sido eliminada de tus favoritos')

    # Devuelve solo el fragmento del ícono actualizado
    return HttpResponse(render_to_string('partials/favorite_icon.html', {'movie_id': movie_id, 'favorite': False}))


@login_required
def add_to_watchlist_partial(request, movie_id):
    """
    Añade una película a la watchlist del usuario y devuelve solo el fragmento del ícono actualizado.
    """
    movie = MovieRequests.get_movie_details(movie_id)

    # Crear o actualizar el elemento en la watchlist
    watchlist_item, created = WatchlistItem.objects.get_or_create(
        profile=request.user.profile,
        movie_id=movie_id,
        defaults={'title': movie.get('title', ''), 'poster_path': movie.get('poster_path')}
    )

    if created:
        messages.success(request, f'"{movie.get("title", "Película")}" ha sido añadida a tu watchlist')
    else:
        messages.info(request, f'"{movie.get("title", "Película")}" ya estaba en tu watchlist')

    # Devuelve solo el fragmento del ícono actualizado
    return HttpResponse(render_to_string('partials/watchlist_icon.html', {'movie_id': movie_id, 'watchlist': True}))


@login_required
def remove_from_watchlist_partial(request, movie_id):
    """
    Elimina una película de la watchlist del usuario y devuelve solo el fragmento del ícono actualizado.
    """
    watchlist_item = get_object_or_404(WatchlistItem, profile=request.user.profile, movie_id=movie_id)
    watchlist_item.delete()

    # Devuelve solo el fragmento del ícono actualizado
    return HttpResponse(render_to_string('partials/watchlist_icon.html', {'movie_id': movie_id, 'watchlist': False}))
