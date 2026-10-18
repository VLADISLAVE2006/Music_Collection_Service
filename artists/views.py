"""Страницы исполнителей: данные получаются SQL-запросами из SQLite."""
import sqlite3
from contextlib import closing

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def artists(request: HttpRequest) -> HttpResponse:
    """Список исполнителей с количеством альбомов."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        artists_data = conn.execute("""
            SELECT
                artists.id,
                artists.name,
                artists.country,
                artists.genre,
                COUNT(albums.id) AS albums_count
            FROM artists
            LEFT JOIN albums ON albums.artist_id = artists.id
            GROUP BY artists.id, artists.name, artists.country, artists.genre
            ORDER BY artists.name;
            """).fetchall()
    return render(
        request,
        "artists/artist_list.html",
        {"artists": artists_data},
    )


def artist_detail(request: HttpRequest, artist_id: int) -> HttpResponse:
    """Карточка исполнителя и его альбомы; при отсутствии — код 404."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        artist = conn.execute("""
            SELECT
                id,
                name,
                country,
                genre
            FROM artists
            WHERE id = ?;
            """, [artist_id]).fetchone()
        albums_data = conn.execute("""
            SELECT
                id,
                title,
                release_year
            FROM albums
            WHERE artist_id = ?
            ORDER BY release_year, title;
            """, [artist_id]).fetchall()
    return render(
        request,
        "artists/artist_detail.html",
        {"artist": artist, "albums": albums_data},
        status=404 if artist is None else 200,
    )
