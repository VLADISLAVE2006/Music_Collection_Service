"""Функции работы с коллекциями.

Коллекция — словарь: {"id", "user_id", "album_ids"}, где album_ids —
список идентификаторов альбомов пользователя.
"""
from typing import Dict, List, Optional

from albums import create_album, get_rating_stars
from utils import next_id


def create_collection(collections: List[Dict], user_id: int) -> Dict:
    """Создать пустую коллекцию пользователя и добавить в список."""
    collection = {
        "id": next_id(collections),
        "user_id": user_id,
        "album_ids": [],
    }
    collections.append(collection)
    return collection


def get_user_collection(
    collections: List[Dict],
    user_id: int,
) -> Optional[Dict]:
    """Найти коллекцию пользователя (у пользователя она одна)."""
    for collection in collections:
        if collection["user_id"] == user_id:
            return collection
    return None


def get_collection_albums(
    collection: Dict,
    albums: List[Dict],
) -> List[Dict]:
    """Вернуть альбомы, входящие в коллекцию, в порядке добавления."""
    by_id = {album["id"]: album for album in albums}
    return [
        by_id[album_id]
        for album_id in collection["album_ids"]
        if album_id in by_id
    ]


def is_album_in_collection(
    collection_albums: List[Dict],
    title: str,
    artist_id: int,
) -> bool:
    """Проверить, есть ли альбом с таким названием этого исполнителя."""
    title = title.strip().lower()
    return any(
        album["title"].lower() == title and album["artist_id"] == artist_id
        for album in collection_albums
    )


def add_album_to_collection(
    collection: Dict,
    albums: List[Dict],
    title: str,
    artist_id: int,
    release_year: int,
    genre: str,
    songs_count: int = 0,
) -> Optional[Dict]:
    """Создать альбом и добавить его в коллекцию и общий список альбомов.

    Возвращает созданный альбом или None, если такой альбом уже есть
    в коллекции. При нарушении бизнес-правил выбрасывает ValueError.
    """
    album = create_album(
        next_id(albums),
        title,
        artist_id,
        release_year,
        genre,
        collection["user_id"],
        songs_count,
    )
    if is_album_in_collection(
        get_collection_albums(collection, albums), title, artist_id
    ):
        return None
    albums.append(album)
    collection["album_ids"].append(album["id"])
    return album


def remove_album_from_collection(
    collection: Dict,
    albums: List[Dict],
    album_id: int,
) -> bool:
    """Удалить альбом из коллекции и из общего списка альбомов."""
    if album_id not in collection["album_ids"]:
        return False
    collection["album_ids"].remove(album_id)
    albums[:] = [album for album in albums if album["id"] != album_id]
    return True


def get_statistics(collection_albums: List[Dict]) -> Dict:
    """Посчитать статистику по альбомам коллекции."""
    ratings = [a["rating"] for a in collection_albums if a["rating"]]
    return {
        "total_albums": len(collection_albums),
        "total_songs": sum(a["songs_count"] for a in collection_albums),
        "total_artists": len({a["artist_id"] for a in collection_albums}),
        "listened_count": sum(1 for a in collection_albums
                              if a["is_listened"]),
        "average_rating": (
            sum(ratings) / len(ratings) if ratings else None
        ),
    }


def get_favorite_genre(collection_albums: List[Dict]) -> Optional[str]:
    """Вернуть жанр с наивысшей средней оценкой (None, если оценок нет)."""
    ratings_by_genre: Dict[str, List[int]] = {}
    for album in collection_albums:
        if album["rating"] is not None:
            ratings_by_genre.setdefault(album["genre"], []).append(
                album["rating"]
            )
    if not ratings_by_genre:
        return None
    return max(
        ratings_by_genre,
        key=lambda genre: (
            sum(ratings_by_genre[genre]) / len(ratings_by_genre[genre])
        ),
    )


def get_collection_recommendation(collection_albums: List[Dict]) -> str:
    """Сформировать рекомендацию на основе оценок коллекции."""
    genre = get_favorite_genre(collection_albums)
    if genre is None:
        return "Оцените несколько альбомов, чтобы получить рекомендацию"
    return (
        f"Если вам нравится {genre}, "
        "советуем послушать похожие альбомы!"
    )


def show_statistics(collection_albums: List[Dict]) -> None:
    """Вывести общую статистику коллекции."""
    stats = get_statistics(collection_albums)
    average = stats["average_rating"]
    print(" Статистика коллекции:")
    print(f" Всего песен: {stats['total_songs']}")
    print(f" Всего альбомов: {stats['total_albums']}")
    print(f" Всего исполнителей: {stats['total_artists']}")
    print(f" Прослушано альбомов: {stats['listened_count']}")
    if average is None:
        print(" Средняя оценка: нет оценок")
    else:
        stars = get_rating_stars(round(average))
        print(f" Средняя оценка: {stars} ({average:.1f}/5)")
