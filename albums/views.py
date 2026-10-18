"""Страницы альбомов: данные получаются SQL-запросами из SQLite."""
import sqlite3
from contextlib import closing
from types import SimpleNamespace

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.albums import (
    MAX_RATING,
    MIN_RATING,
    get_album_status,
    get_recommendation,
)


def albums(request: HttpRequest) -> HttpResponse:
    """Список всех альбомов с исполнителями."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        albums_data = conn.execute("""
            SELECT
                albums.id,
                albums.title,
                albums.release_year,
                albums.genre,
                artists.name AS artist_name,
                albums.rating,
                albums.is_listened
            FROM albums
            JOIN artists ON albums.artist_id = artists.id
            ORDER BY albums.title;
            """).fetchall()
    return render(
        request,
        "albums/album_list.html",
        {"albums": albums_data},
    )


def album_detail(request: HttpRequest, album_id: int) -> HttpResponse:
    """Карточка альбома; если альбом не найден, код ответа 404."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT
                albums.id,
                albums.title,
                albums.release_year,
                albums.genre,
                albums.songs_count,
                albums.rating,
                albums.is_listened,
                artists.id AS artist_id,
                artists.name AS artist_name,
                users.name AS owner_name,
                CAST(strftime('%Y', 'now') AS INTEGER)
                    - albums.release_year AS age
            FROM albums
            JOIN artists ON albums.artist_id = artists.id
            JOIN users ON albums.user_id = users.id
            WHERE albums.id = ?;
            """, [album_id]).fetchone()
    context = {"album": None, "max_rating": MAX_RATING}
    if row is not None:
        album = SimpleNamespace(**dict(row))
        context["album"] = album
        context["status"] = get_album_status(album)
        context["recommendation"] = get_recommendation(album)
    return render(
        request,
        "albums/album_detail.html",
        context,
        status=404 if row is None else 200,
    )


def search(request: HttpRequest) -> HttpResponse:
    """Поиск альбомов по жанру, минимальной оценке и части названия."""
    genre = request.GET.get("genre", "").strip()
    title = request.GET.get("title", "").strip()
    try:
        min_rating = int(request.GET.get("min_rating", "0"))
    except ValueError:
        min_rating = 0
    min_rating = max(0, min(min_rating, MAX_RATING))
    submitted = bool(request.GET)
    found = []
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        genres = conn.execute("""
            SELECT DISTINCT genre
            FROM albums
            ORDER BY genre;
            """).fetchall()
        if submitted:
            found = conn.execute("""
                SELECT
                    albums.id,
                    albums.title,
                    albums.release_year,
                    albums.genre,
                    artists.name AS artist_name,
                    albums.rating,
                    albums.is_listened
                FROM albums
                JOIN artists ON albums.artist_id = artists.id
                WHERE (? = '' OR albums.genre = ?)
                  AND COALESCE(albums.rating, 0) >= ?
                  AND albums.title LIKE '%' || ? || '%'
                ORDER BY albums.title;
                """, [genre, genre, min_rating, title]).fetchall()
    context = {
        "albums": found,
        "genres": genres,
        "genre": genre,
        "title": title,
        "min_rating": min_rating,
        "ratings": range(MIN_RATING - 1, MAX_RATING + 1),
        "submitted": submitted,
    }
    return render(request, "albums/search.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Статистика альбомов: общие показатели, жанры, исполнители."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        totals = conn.execute("""
            SELECT
                COUNT(*) AS albums_count,
                COUNT(albums.rating) AS rated_count,
                AVG(albums.rating) AS average_rating,
                COALESCE(SUM(albums.songs_count), 0) AS songs_count
            FROM albums;
            """).fetchone()
        genres = conn.execute("""
            SELECT
                albums.genre,
                COUNT(*) AS albums_count,
                AVG(albums.rating) AS average_rating,
                SUM(albums.songs_count) AS songs_count
            FROM albums
            GROUP BY albums.genre
            ORDER BY albums_count DESC, albums.genre;
            """).fetchall()
        artists = conn.execute("""
            SELECT
                artists.name AS artist_name,
                COUNT(albums.id) AS albums_count
            FROM artists
            JOIN albums ON albums.artist_id = artists.id
            GROUP BY artists.id, artists.name
            HAVING COUNT(albums.id) > 1
            ORDER BY albums_count DESC, artists.name;
            """).fetchall()
    context = {
        "totals": totals,
        "genres": genres,
        "artists": artists,
        "max_rating": MAX_RATING,
    }
    return render(request, "albums/statistics.html", context)
