"""Страницы музыкальных коллекций пользователей."""
from html import escape

from django.http import HttpRequest, HttpResponse

from homepage.views import not_found, page
from main import load_data
from models.albums import MAX_RATING, get_rating_stars
from models.collection import (
    find_collection_by_id,
    get_collection_recommendation,
)


def collections(request: HttpRequest) -> HttpResponse:
    """Список коллекций всех пользователей."""
    _, _, _, collections_list = load_data()
    items = ""
    for collection in collections_list:
        text = escape(f"Коллекция пользователя {collection.user.name}")
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/collections/{collection.id}/">{text}</a>
            <span class="badge bg-primary">
                альбомов: {collection.total_albums}
            </span>
        </li>
        """
    content = f"""
    <h1>Коллекции</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Maestro — коллекции", content))


def collection_detail(
    request: HttpRequest,
    collection_id: int,
) -> HttpResponse:
    """Коллекция: статистика и альбомы; при отсутствии — код 404."""
    _, _, _, collections_list = load_data()
    collection = find_collection_by_id(collections_list, collection_id)
    if collection is None:
        return not_found(
            "Коллекция не найдена", "/collections/", "к списку коллекций"
        )
    average = collection.average_rating
    average_text = (
        f"{get_rating_stars(round(average))} ({average:.1f}/{MAX_RATING})"
        if average is not None else "нет оценок"
    )
    items = ""
    for album in collection.albums:
        text = escape(f"{album.title} — {album.artist.name}")
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/albums/{album.id}/">{text}</a>
            <span>{get_rating_stars(album.rating)}</span>
        </li>
        """
    albums_block = (
        f'<ul class="list-group">{items}</ul>' if items
        else '<p class="text-muted">В коллекции пока нет альбомов.</p>'
    )
    content = f"""
    <h1>Коллекция: {escape(collection.user.name)}</h1>
    <div class="card mb-3">
        <div class="card-body">
            <p class="card-text">
                <strong>Всего альбомов:</strong> {collection.total_albums}
            </p>
            <p class="card-text">
                <strong>Всего песен:</strong> {collection.total_songs}
            </p>
            <p class="card-text">
                <strong>Исполнителей:</strong> {collection.total_artists}
            </p>
            <p class="card-text">
                <strong>Прослушано:</strong> {collection.listened_count}
            </p>
            <p class="card-text">
                <strong>Средняя оценка:</strong> {average_text}
            </p>
            <p class="card-text">
                {escape(get_collection_recommendation(collection))}
            </p>
        </div>
    </div>
    {albums_block}
    <a href="/collections/" class="btn btn-outline-secondary mt-3">
        ← к списку коллекций
    </a>
    """
    return HttpResponse(page(f"Коллекция: {collection.user.name}", content))
