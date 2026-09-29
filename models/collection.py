"""Класс коллекции и функции работы с коллекциями."""
from typing import Dict, List, Optional

from utils import next_id

from .albums import Album, get_rating_stars
from .artists import Artist
from .users import User


class Collection:
    """Музыкальная коллекция пользователя."""

    def __init__(
        self,
        collection_id: int,
        user: User,
        albums: Optional[List[Album]] = None,
    ) -> None:
        """Создать коллекцию пользователя."""
        self.id = collection_id
        self.user = user
        self.albums: List[Album] = list(albums) if albums else []

    def contains(self, album: Album) -> bool:
        """Проверить, есть ли такой альбом в коллекции.

        Альбомом-дубликатом считается альбом с тем же идентификатором
        или с тем же названием того же исполнителя.
        """
        title = album.title.lower()
        return any(
            existing.id == album.id
            or (
                existing.title.lower() == title
                and existing.artist.id == album.artist.id
            )
            for existing in self.albums
        )

    def add_album(self, album: Album) -> None:
        """Добавить альбом в коллекцию.

        Raises:
            ValueError: если альбом принадлежит другому пользователю
                или уже есть в коллекции.
        """
        if album.user.id != self.user.id:
            raise ValueError("Альбом принадлежит другому пользователю")
        if self.contains(album):
            raise ValueError("Этот альбом уже есть в коллекции")
        self.albums.append(album)

    def remove_album(self, album_id: int) -> bool:
        """Удалить альбом из коллекции; вернуть True, если он был найден."""
        for album in self.albums:
            if album.id == album_id:
                self.albums.remove(album)
                return True
        return False

    @property
    def total_albums(self) -> int:
        """Количество альбомов."""
        return len(self.albums)

    @property
    def total_songs(self) -> int:
        """Общее количество песен во всех альбомах."""
        return sum(album.songs_count for album in self.albums)

    @property
    def total_artists(self) -> int:
        """Количество различных исполнителей."""
        return len({album.artist.id for album in self.albums})

    @property
    def listened_count(self) -> int:
        """Количество прослушанных альбомов."""
        return sum(1 for album in self.albums if album.is_listened)

    @property
    def average_rating(self) -> Optional[float]:
        """Средняя оценка оценённых альбомов (None, если оценок нет)."""
        ratings = [a.rating for a in self.albums if a.rating is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)

    def favorite_genre(self) -> Optional[str]:
        """Вернуть жанр с наивысшей средней оценкой (None, если оценок нет)."""
        ratings_by_genre: Dict[str, List[int]] = {}
        for album in self.albums:
            if album.rating is not None:
                ratings_by_genre.setdefault(album.genre, []).append(
                    album.rating
                )
        if not ratings_by_genre:
            return None
        return max(
            ratings_by_genre,
            key=lambda genre: (
                sum(ratings_by_genre[genre]) / len(ratings_by_genre[genre])
            ),
        )

    def __str__(self) -> str:
        """Строковое представление коллекции."""
        return (
            f"Коллекция #{self.id} пользователя {self.user.name}: "
            f"альбомов — {self.total_albums}"
        )


def create_collection(
    collections: List[Collection],
    user: User,
) -> Collection:
    """Создать пустую коллекцию пользователя и добавить в список."""
    collection = Collection(next_id(collections), user)
    collections.append(collection)
    return collection


def get_user_collection(
    collections: List[Collection],
    user: User,
) -> Optional[Collection]:
    """Найти коллекцию пользователя (у пользователя она одна)."""
    for collection in collections:
        if collection.user.id == user.id:
            return collection
    return None


def add_album_to_collection(
    collection: Collection,
    albums: List[Album],
    title: str,
    artist: Artist,
    release_year: int,
    genre: str,
    songs_count: int = 0,
) -> Optional[Album]:
    """Создать альбом и добавить его в коллекцию и общий список альбомов.

    Возвращает созданный альбом или None, если такой альбом уже есть
    в коллекции. При нарушении бизнес-правил выбрасывает ValueError.
    """
    album = Album(
        next_id(albums),
        title,
        artist,
        release_year,
        genre,
        collection.user,
        songs_count,
    )
    if collection.contains(album):
        return None
    collection.add_album(album)
    albums.append(album)
    return album


def remove_album_from_collection(
    collection: Collection,
    albums: List[Album],
    album_id: int,
) -> bool:
    """Удалить альбом из коллекции и из общего списка альбомов."""
    if not collection.remove_album(album_id):
        return False
    albums[:] = [album for album in albums if album.id != album_id]
    return True


def get_collection_recommendation(collection: Collection) -> str:
    """Сформировать рекомендацию на основе оценок коллекции."""
    genre = collection.favorite_genre()
    if genre is None:
        return "Оцените несколько альбомов, чтобы получить рекомендацию"
    return (
        f"Если вам нравится {genre}, "
        "советуем послушать похожие альбомы!"
    )


def show_statistics(collection: Collection) -> None:
    """Вывести общую статистику коллекции."""
    average = collection.average_rating
    print(" Статистика коллекции:")
    print(f" Всего песен: {collection.total_songs}")
    print(f" Всего альбомов: {collection.total_albums}")
    print(f" Всего исполнителей: {collection.total_artists}")
    print(f" Прослушано альбомов: {collection.listened_count}")
    if average is None:
        print(" Средняя оценка: нет оценок")
    else:
        stars = get_rating_stars(round(average))
        print(f" Средняя оценка: {stars} ({average:.1f}/5)")
