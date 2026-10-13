"""Страницы альбомов."""
from html import escape

from django.http import HttpRequest, HttpResponse

from homepage.views import not_found, page
from main import load_data
from models.albums import (
    MAX_RATING,
    find_album_by_id,
    get_album_status,
    get_rating_stars,
    get_recommendation,
)


def albums(request: HttpRequest) -> HttpResponse:
    """Список всех альбомов."""
    _, _, albums_list, _ = load_data()
    items = ""
    for album in albums_list:
        text = escape(f"{album.title} — {album.artist.name}")
        stars = get_rating_stars(album.rating)
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/albums/{album.id}/">{text}</a>
            <span>{stars}</span>
        </li>
        """
    content = f"""
    <h1>Альбомы</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Maestro — альбомы", content))


def album_detail(request: HttpRequest, album_id: int) -> HttpResponse:
    """Карточка альбома; если альбом не найден, код ответа 404."""
    _, _, albums_list, _ = load_data()
    album = find_album_by_id(albums_list, album_id)
    if album is None:
        return not_found("Альбом не найден", "/albums/", "к списку альбомов")
    rating = (
        f"{album.rating}/{MAX_RATING}" if album.rating is not None
        else "нет оценки"
    )
    badge = "bg-success" if album.is_listened else "bg-secondary"
    listened = "прослушан" if album.is_listened else "не прослушан"
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(album.title)}</h5>
            <p class="card-text">
                <strong>Исполнитель:</strong>
                <a href="/artists/{album.artist.id}/">
                    {escape(album.artist.name)}
                </a>
            </p>
            <p class="card-text">
                <strong>Год выпуска:</strong> {album.release_year}
                ({album.age()} лет назад)
            </p>
            <p class="card-text">
                <strong>Жанр:</strong> {escape(album.genre)}
            </p>
            <p class="card-text">
                <strong>Песен:</strong> {album.songs_count}
            </p>
            <p class="card-text">
                <strong>Оценка:</strong>
                {get_rating_stars(album.rating)} ({rating})
            </p>
            <p class="card-text">
                <strong>Статус:</strong> {escape(get_album_status(album))}
                <span class="badge {badge}">{listened}</span>
            </p>
            <p class="card-text">{escape(get_recommendation(album))}</p>
            <p class="card-text text-muted">
                Владелец: {escape(album.user.name)}
            </p>
            <a href="/albums/" class="btn btn-outline-secondary">
                ← к списку альбомов
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(album.title, content))
