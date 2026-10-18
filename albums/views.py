"""Страницы альбомов."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from main import load_data
from models.albums import (
    MAX_RATING,
    find_album_by_id,
    get_album_status,
    get_recommendation,
)


def albums(request: HttpRequest) -> HttpResponse:
    """Список всех альбомов."""
    _, _, albums_list, _ = load_data()
    context = {
        "albums": albums_list,
    }
    return render(request, "albums/album_list.html", context)


def album_detail(request: HttpRequest, album_id: int) -> HttpResponse:
    """Карточка альбома; если альбом не найден, код ответа 404."""
    _, _, albums_list, _ = load_data()
    album = find_album_by_id(albums_list, album_id)
    context = {
        "album": album,
        "max_rating": MAX_RATING,
    }
    if album is not None:
        context["status"] = get_album_status(album)
        context["recommendation"] = get_recommendation(album)
    return render(
        request,
        "albums/album_detail.html",
        context,
        status=404 if album is None else 200,
    )
