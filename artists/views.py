"""Страницы исполнителей."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from main import load_data
from models.artists import find_artist_by_id


def artists(request: HttpRequest) -> HttpResponse:
    """Список всех исполнителей."""
    _, artists_list, _, _ = load_data()
    context = {
        "artists": artists_list,
    }
    return render(request, "artists/artist_list.html", context)


def artist_detail(request: HttpRequest, artist_id: int) -> HttpResponse:
    """Карточка исполнителя и его альбомы; при отсутствии — код 404."""
    _, artists_list, albums_list, _ = load_data()
    artist = find_artist_by_id(artists_list, artist_id)
    context = {
        "artist": artist,
        "albums": [
            album for album in albums_list
            if artist is not None and album.artist.id == artist.id
        ],
    }
    return render(
        request,
        "artists/artist_detail.html",
        context,
        status=404 if artist is None else 200,
    )
