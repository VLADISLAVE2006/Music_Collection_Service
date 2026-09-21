"""Функции работы с исполнителями.

Исполнитель — словарь: {"id", "name", "country", "genre"}.
"""
from typing import Dict, List, Optional

from utils import next_id


def add_artist(
    artists: List[Dict],
    name: str,
    country: str,
    genre: str,
) -> Dict:
    """Добавить исполнителя в список и вернуть созданную запись.

    Raises:
        ValueError: если имя исполнителя пустое.
    """
    if not name.strip():
        raise ValueError("Имя исполнителя не может быть пустым")
    artist = {
        "id": next_id(artists),
        "name": name.strip(),
        "country": country.strip(),
        "genre": genre.strip(),
    }
    artists.append(artist)
    return artist


def find_artist(artists: List[Dict], query: str) -> List[Dict]:
    """Найти исполнителей по подстроке имени (без учёта регистра)."""
    query = query.strip().lower()
    return [artist for artist in artists if query in artist["name"].lower()]


def find_artist_by_id(
    artists: List[Dict],
    artist_id: int,
) -> Optional[Dict]:
    """Найти исполнителя по идентификатору."""
    for artist in artists:
        if artist["id"] == artist_id:
            return artist
    return None


def find_artist_by_name(
    artists: List[Dict],
    name: str,
) -> Optional[Dict]:
    """Найти исполнителя по точному имени (без учёта регистра)."""
    name = name.strip().lower()
    for artist in artists:
        if artist["name"].lower() == name:
            return artist
    return None


def get_artist_name(artists: List[Dict], artist_id: int) -> str:
    """Вернуть имя исполнителя по идентификатору."""
    artist = find_artist_by_id(artists, artist_id)
    return artist["name"] if artist else "Неизвестный исполнитель"


def show_artists(artists: List[Dict]) -> None:
    """Вывести список исполнителей."""
    if not artists:
        print("Список исполнителей пуст.")
        return
    for artist in artists:
        print(
            f"[{artist['id']}] {artist['name']} ({artist['country']}), "
            f"жанр: {artist['genre']}"
        )
