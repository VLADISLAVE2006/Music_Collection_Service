"""Класс альбома и функции работы с альбомами."""
from datetime import date
from typing import List, Optional

from .artists import Artist
from .users import User

MIN_RATING = 1
MAX_RATING = 5
MIN_RELEASE_YEAR = 1900


def get_rating_stars(rating: Optional[int]) -> str:
    """Вернуть оценку в виде звёзд, например ★★★★☆."""
    stars = rating or 0
    return "★" * stars + "☆" * (MAX_RATING - stars)


class Album:
    """Музыкальный альбом пользователя."""

    def __init__(
        self,
        album_id: int,
        title: str,
        artist: Artist,
        release_year: int,
        genre: str,
        user: User,
        songs_count: int = 0,
        rating: Optional[int] = None,
        is_listened: bool = False,
    ) -> None:
        """Создать альбом.

        Raises:
            ValueError: при нарушении бизнес-правил (пустое название,
                год выпуска в будущем, оценка вне диапазона 1-5).
        """
        if not title.strip():
            raise ValueError("Название альбома не может быть пустым")
        if not Album.validate_year(release_year):
            raise ValueError(
                f"Год выпуска должен быть от {MIN_RELEASE_YEAR} "
                f"до {date.today().year}"
            )
        if songs_count < 0:
            raise ValueError("Количество песен не может быть отрицательным")
        if rating is not None and not Album.validate_rating(rating):
            raise ValueError(
                f"Оценка должна быть от {MIN_RATING} до {MAX_RATING}"
            )
        self.id = album_id
        self.title = title.strip()
        self.artist = artist
        self.release_year = release_year
        self.genre = genre.strip()
        self.user = user
        self.songs_count = songs_count
        self.rating = rating
        self.is_listened = is_listened

    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Проверить, что оценка находится в диапазоне от 1 до 5."""
        return MIN_RATING <= rating <= MAX_RATING

    @staticmethod
    def validate_year(year: int) -> bool:
        """Проверить, что год выпуска не находится в будущем."""
        return MIN_RELEASE_YEAR <= year <= date.today().year

    def mark_listened(self) -> None:
        """Отметить альбом как прослушанный."""
        self.is_listened = True

    def rate(self, rating: int) -> None:
        """Поставить оценку (1-5); оценённый альбом считается прослушанным.

        Raises:
            ValueError: если оценка вне диапазона.
        """
        if not Album.validate_rating(rating):
            raise ValueError(
                f"Оценка должна быть от {MIN_RATING} до {MAX_RATING}"
            )
        self.rating = rating
        self.is_listened = True

    def age(self) -> int:
        """Вернуть возраст альбома в годах."""
        return date.today().year - self.release_year

    @property
    def rating_stars(self) -> str:
        """Оценка альбома в виде звёзд (для шаблонов)."""
        return get_rating_stars(self.rating)

    def __str__(self) -> str:
        """Строковое представление альбома."""
        listened = "прослушан" if self.is_listened else "не прослушан"
        return (
            f"{self.title} — {self.artist.name} ({self.release_year}), "
            f"{self.genre}, {get_rating_stars(self.rating)}, {listened}"
        )


def get_album_status(album: Album) -> str:
    """Вернуть текстовый статус альбома (функция из ПР1)."""
    if not album.is_listened:
        return "Еще не прослушан"
    if album.rating is None:
        return "Прослушан, но не оценён"
    if album.rating >= 4:
        return "Отличный альбом! Рекомендую!"
    if album.rating >= 3:
        return "Хороший альбом, стоит послушать"
    return "Прослушан, но не впечатлил"


def get_recommendation(album: Album) -> str:
    """Вернуть рекомендацию по альбому (функция из ПР1)."""
    if album.rating is None:
        return "Оцените альбом, чтобы получить рекомендацию"
    if album.rating >= 4:
        return (
            f"Если вам нравится {album.genre}, "
            "советуем послушать похожие альбомы!"
        )
    return "Попробуйте другие жанры, возможно, найдете что-то интереснее"


def find_album(albums: List[Album], query: str) -> List[Album]:
    """Найти альбомы по подстроке названия или имени исполнителя."""
    query = query.strip().lower()
    return [
        album for album in albums
        if query in album.title.lower() or query in album.artist.name.lower()
    ]


def find_album_by_id(albums: List[Album], album_id: int) -> Optional[Album]:
    """Найти альбом по идентификатору."""
    for album in albums:
        if album.id == album_id:
            return album
    return None


def filter_albums_by_genre(albums: List[Album], genre: str) -> List[Album]:
    """Отобрать альбомы указанного жанра (без учёта регистра)."""
    genre = genre.strip().lower()
    return list(album for album in albums if album.genre.lower() == genre)


def sort_albums(albums: List[Album], by: str = "rating") -> List[Album]:
    """Отсортировать альбомы по оценке, году выпуска или названию.

    Raises:
        ValueError: если указан неизвестный критерий сортировки.
    """
    if by == "rating":
        return sorted(albums, key=lambda a: a.rating or 0, reverse=True)
    if by == "year":
        return sorted(albums, key=lambda a: a.release_year)
    if by == "title":
        return sorted(albums, key=lambda a: a.title.lower())
    raise ValueError(f"Неизвестный критерий сортировки: {by}")


def show_albums(albums: List[Album]) -> None:
    """Вывести список альбомов."""
    if not albums:
        print("Список альбомов пуст.")
        return
    for album in albums:
        print(f"[{album.id}] {album}")
