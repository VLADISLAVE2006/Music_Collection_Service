"""Функции работы с альбомами.

Альбом — словарь: {"id", "title", "artist_id", "release_year", "genre",
"songs_count", "rating", "is_listened", "user_id"}.
Оценка None означает, что альбом ещё не оценён.
"""
from datetime import date
from typing import Dict, List, Optional

MIN_RATING = 1
MAX_RATING = 5
MIN_RELEASE_YEAR = 1900


def validate_rating(rating: int) -> bool:
    """Проверить, что оценка находится в диапазоне от 1 до 5."""
    return MIN_RATING <= rating <= MAX_RATING


def validate_year(year: int) -> bool:
    """Проверить, что год выпуска не находится в будущем."""
    return MIN_RELEASE_YEAR <= year <= date.today().year


def create_album(
    album_id: int,
    title: str,
    artist_id: int,
    release_year: int,
    genre: str,
    user_id: int,
    songs_count: int = 0,
) -> Dict:
    """Создать запись альбома, проверив бизнес-правила.

    Raises:
        ValueError: при пустом названии, недопустимом годе выпуска
            или отрицательном количестве песен.
    """
    if not title.strip():
        raise ValueError("Название альбома не может быть пустым")
    if not validate_year(release_year):
        raise ValueError(
            f"Год выпуска должен быть от {MIN_RELEASE_YEAR} "
            f"до {date.today().year}"
        )
    if songs_count < 0:
        raise ValueError("Количество песен не может быть отрицательным")
    return {
        "id": album_id,
        "title": title.strip(),
        "artist_id": artist_id,
        "release_year": release_year,
        "genre": genre.strip(),
        "songs_count": songs_count,
        "rating": None,
        "is_listened": False,
        "user_id": user_id,
    }


def get_rating_stars(rating: Optional[int]) -> str:
    """Вернуть оценку в виде звёзд, например ★★★★☆."""
    stars = rating or 0
    return "★" * stars + "☆" * (MAX_RATING - stars)


def get_album_status(is_listened: bool, rating: Optional[int]) -> str:
    """Вернуть текстовый статус альбома (функция из ПР1)."""
    if not is_listened:
        return "Еще не прослушан"
    if rating is None:
        return "Прослушан, но не оценён"
    if rating >= 4:
        return "Отличный альбом! Рекомендую!"
    if rating >= 3:
        return "Хороший альбом, стоит послушать"
    return "Прослушан, но не впечатлил"


def get_recommendation(genre: str, rating: Optional[int]) -> str:
    """Вернуть рекомендацию по альбому (функция из ПР1)."""
    if rating is None:
        return "Оцените альбом, чтобы получить рекомендацию"
    if rating >= 4:
        return (
            f"Если вам нравится {genre}, "
            "советуем послушать похожие альбомы!"
        )
    return "Попробуйте другие жанры, возможно, найдете что-то интереснее"


def get_album_age(album: Dict) -> int:
    """Вернуть возраст альбома в годах."""
    return date.today().year - album["release_year"]


def rate_album(album: Dict, rating: int) -> None:
    """Поставить оценку (1-5); оценённый альбом считается прослушанным.

    Raises:
        ValueError: если оценка вне диапазона.
    """
    if not validate_rating(rating):
        raise ValueError(
            f"Оценка должна быть от {MIN_RATING} до {MAX_RATING}"
        )
    album["rating"] = rating
    album["is_listened"] = True


def mark_album_listened(album: Dict) -> None:
    """Отметить альбом как прослушанный."""
    album["is_listened"] = True


def find_album(
    albums: List[Dict],
    artists: List[Dict],
    query: str,
) -> List[Dict]:
    """Найти альбомы по подстроке названия или имени исполнителя."""
    query = query.strip().lower()
    names = {artist["id"]: artist["name"].lower() for artist in artists}
    return [
        album for album in albums
        if query in album["title"].lower()
        or query in names.get(album["artist_id"], "")
    ]


def find_album_by_id(albums: List[Dict], album_id: int) -> Optional[Dict]:
    """Найти альбом по идентификатору."""
    for album in albums:
        if album["id"] == album_id:
            return album
    return None


def filter_albums_by_genre(albums: List[Dict], genre: str) -> List[Dict]:
    """Отобрать альбомы указанного жанра (без учёта регистра)."""
    genre = genre.strip().lower()
    return list(album for album in albums if album["genre"].lower() == genre)


def sort_albums(albums: List[Dict], by: str = "rating") -> List[Dict]:
    """Отсортировать альбомы по оценке, году выпуска или названию.

    Raises:
        ValueError: если указан неизвестный критерий сортировки.
    """
    if by == "rating":
        return sorted(albums, key=lambda a: a["rating"] or 0, reverse=True)
    if by == "year":
        return sorted(albums, key=lambda a: a["release_year"])
    if by == "title":
        return sorted(albums, key=lambda a: a["title"].lower())
    raise ValueError(f"Неизвестный критерий сортировки: {by}")


def format_album(album: Dict, artists: List[Dict]) -> str:
    """Сформировать строку с описанием альбома."""
    artist = next(
        (a["name"] for a in artists if a["id"] == album["artist_id"]),
        "Неизвестный исполнитель",
    )
    listened = "прослушан" if album["is_listened"] else "не прослушан"
    return (
        f"{album['title']} — {artist} ({album['release_year']}), "
        f"{album['genre']}, {get_rating_stars(album['rating'])}, {listened}"
    )


def show_albums(albums: List[Dict], artists: List[Dict]) -> None:
    """Вывести список альбомов."""
    if not albums:
        print("Список альбомов пуст.")
        return
    for album in albums:
        print(f"[{album['id']}] {format_album(album, artists)}")
