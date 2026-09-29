"""Класс исполнителя и функции работы с исполнителями."""
from typing import List, Optional

from utils import next_id


class Artist:
    """Исполнитель музыкальных альбомов."""

    def __init__(
        self,
        artist_id: int,
        name: str,
        country: str,
        genre: str,
    ) -> None:
        """Создать исполнителя.

        Raises:
            ValueError: если имя исполнителя пустое.
        """
        if not name.strip():
            raise ValueError("Имя исполнителя не может быть пустым")
        self.id = artist_id
        self.name = name.strip()
        self.country = country.strip()
        self.genre = genre.strip()

    @classmethod
    def from_data(cls, data: dict) -> "Artist":
        """Создать исполнителя из словаря (запись JSON)."""
        return cls(
            artist_id=data["id"],
            name=data["name"],
            country=data["country"],
            genre=data["genre"],
        )

    def __str__(self) -> str:
        """Строковое представление исполнителя."""
        return f"{self.name} ({self.country}), жанр: {self.genre}"


def add_artist(
    artists: List[Artist],
    name: str,
    country: str,
    genre: str,
) -> Artist:
    """Создать исполнителя, добавить в коллекцию и вернуть его."""
    artist = Artist(next_id(artists), name, country, genre)
    artists.append(artist)
    return artist


def find_artist(artists: List[Artist], query: str) -> List[Artist]:
    """Найти исполнителей по подстроке имени (без учёта регистра)."""
    query = query.strip().lower()
    return [artist for artist in artists if query in artist.name.lower()]


def find_artist_by_id(
    artists: List[Artist],
    artist_id: int,
) -> Optional[Artist]:
    """Найти исполнителя по идентификатору."""
    for artist in artists:
        if artist.id == artist_id:
            return artist
    return None


def find_artist_by_name(
    artists: List[Artist],
    name: str,
) -> Optional[Artist]:
    """Найти исполнителя по точному имени (без учёта регистра)."""
    name = name.strip().lower()
    for artist in artists:
        if artist.name.lower() == name:
            return artist
    return None


def show_artists(artists: List[Artist]) -> None:
    """Вывести список исполнителей."""
    if not artists:
        print("Список исполнителей пуст.")
        return
    for artist in artists:
        print(f"[{artist.id}] {artist}")
