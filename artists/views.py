"""Страницы исполнителей."""
from html import escape

from django.http import HttpRequest, HttpResponse

from homepage.views import not_found, page
from main import load_data
from models.artists import find_artist_by_id


def artists(request: HttpRequest) -> HttpResponse:
    """Список всех исполнителей."""
    _, artists_list, _, _ = load_data()
    items = ""
    for artist in artists_list:
        text = escape(f"{artist.name} ({artist.country})")
        items += f"""
        <li class="list-group-item">
            <a href="/artists/{artist.id}/">{text}</a>
        </li>
        """
    content = f"""
    <h1>Исполнители</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Maestro — исполнители", content))


def artist_detail(request: HttpRequest, artist_id: int) -> HttpResponse:
    """Карточка исполнителя и его альбомы; при отсутствии — код 404."""
    _, artists_list, albums_list, _ = load_data()
    artist = find_artist_by_id(artists_list, artist_id)
    if artist is None:
        return not_found(
            "Исполнитель не найден", "/artists/", "к списку исполнителей"
        )
    items = ""
    for album in albums_list:
        if album.artist.id == artist.id:
            text = escape(f"{album.title} ({album.release_year})")
            items += f"""
            <li class="list-group-item">
                <a href="/albums/{album.id}/">{text}</a>
            </li>
            """
    albums_block = (
        f'<ul class="list-group list-group-flush">{items}</ul>' if items
        else '<p class="text-muted">Альбомов пока нет.</p>'
    )
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(artist.name)}</h5>
            <p class="card-text">
                <strong>Страна:</strong> {escape(artist.country)}
            </p>
            <p class="card-text">
                <strong>Жанр:</strong> {escape(artist.genre)}
            </p>
            <h6>Альбомы</h6>
            {albums_block}
            <a href="/artists/" class="btn btn-outline-secondary mt-3">
                ← к списку исполнителей
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(artist.name, content))
