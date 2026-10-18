"""Страницы коллекций: данные получаются SQL-запросами из SQLite."""
import sqlite3
from contextlib import closing
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from models.albums import MAX_RATING, get_rating_stars
from models.collection import recommendation_for_genre


def collections(request: HttpRequest) -> HttpResponse:
    """Список коллекций с владельцами и количеством альбомов."""
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        collections_data = conn.execute("""
            SELECT
                collections.id,
                users.name AS user_name,
                COUNT(collection_albums.album_id) AS albums_count
            FROM collections
            JOIN users ON collections.user_id = users.id
            LEFT JOIN collection_albums
                ON collection_albums.collection_id = collections.id
            GROUP BY collections.id, users.name
            ORDER BY collections.id;
            """).fetchall()
    return render(
        request,
        "library/collection_list.html",
        {"collections": collections_data},
    )


def collection_detail(
    request: HttpRequest,
    collection_id: int,
) -> HttpResponse:
    """Коллекция: статистика и альбомы; при отсутствии — код 404."""
    context = {"collection": None, "max_rating": MAX_RATING}
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT
                collections.id,
                users.name AS user_name,
                users.registered_at
            FROM collections
            JOIN users ON collections.user_id = users.id
            WHERE collections.id = ?;
            """, [collection_id]).fetchone()
        if row is not None:
            context["stats"] = conn.execute("""
                SELECT
                    COUNT(albums.id) AS total_albums,
                    COALESCE(SUM(albums.songs_count), 0) AS total_songs,
                    COUNT(DISTINCT albums.artist_id) AS total_artists,
                    COALESCE(SUM(albums.is_listened), 0) AS listened_count,
                    AVG(albums.rating) AS average_rating
                FROM collection_albums
                JOIN albums ON collection_albums.album_id = albums.id
                WHERE collection_albums.collection_id = ?;
                """, [collection_id]).fetchone()
            favorite = conn.execute("""
                SELECT
                    albums.genre,
                    AVG(albums.rating) AS average_rating
                FROM collection_albums
                JOIN albums ON collection_albums.album_id = albums.id
                WHERE collection_albums.collection_id = ?
                  AND albums.rating IS NOT NULL
                GROUP BY albums.genre
                ORDER BY average_rating DESC, albums.genre
                LIMIT 1;
                """, [collection_id]).fetchone()
            context["albums"] = conn.execute("""
                SELECT
                    albums.id,
                    albums.title,
                    albums.rating,
                    albums.is_listened,
                    artists.name AS artist_name
                FROM collection_albums
                JOIN albums ON collection_albums.album_id = albums.id
                JOIN artists ON albums.artist_id = artists.id
                WHERE collection_albums.collection_id = ?
                ORDER BY albums.title;
                """, [collection_id]).fetchall()
    if row is not None:
        collection = dict(row)
        collection["registered_at"] = date.fromisoformat(
            collection["registered_at"]
        )
        context["collection"] = collection
        average = context["stats"]["average_rating"]
        if average is not None:
            context["average_stars"] = get_rating_stars(round(average))
        context["recommendation"] = recommendation_for_genre(
            favorite["genre"] if favorite is not None else None
        )
    return render(
        request,
        "library/collection_detail.html",
        context,
        status=404 if row is None else 200,
    )
