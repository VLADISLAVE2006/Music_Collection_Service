"""Сервис музыкальных коллекций — консольное приложение (ПР2)."""
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from albums import (
    MAX_RATING,
    MIN_RATING,
    MIN_RELEASE_YEAR,
    filter_albums_by_genre,
    find_album,
    find_album_by_id,
    get_album_age,
    get_album_status,
    get_rating_stars,
    get_recommendation,
    mark_album_listened,
    rate_album,
    show_albums,
    sort_albums,
)
from artists import add_artist, find_artist_by_name, show_artists
from collection import (
    add_album_to_collection,
    create_collection,
    get_collection_albums,
    get_collection_recommendation,
    get_user_collection,
    remove_album_from_collection,
    show_statistics,
)
from storage import (
    load_albums,
    load_artists,
    load_collections,
    load_users,
    save_albums,
    save_artists,
    save_collections,
    save_users,
)
from users import add_user, find_user_by_name
from utils import input_int, input_text

DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"
ARTISTS_FILE = DATA_DIR / "artists.json"
ALBUMS_FILE = DATA_DIR / "albums.json"
COLLECTIONS_FILE = DATA_DIR / "collections.json"

LINE = "=" * 50
THIN_LINE = "-" * 50

MENU = """
1. Показать мою коллекцию
2. Добавить альбом
3. Удалить альбом
4. Оценить альбом
5. Отметить альбом прослушанным
6. Найти альбом
7. Показать альбомы жанра
8. Отсортировать альбомы
9. Карточка альбома
10. Статистика коллекции
11. Получить рекомендацию
12. Показать исполнителей
0. Выход
"""

AppData = Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]


def load_data() -> AppData:
    """Загрузить все данные из JSON-файлов."""
    return (
        load_users(USERS_FILE),
        load_artists(ARTISTS_FILE),
        load_albums(ALBUMS_FILE),
        load_collections(COLLECTIONS_FILE),
    )


def save_data(
    users: List[Dict],
    artists: List[Dict],
    albums: List[Dict],
    collections: List[Dict],
) -> None:
    """Сохранить все данные в JSON-файлы."""
    save_users(USERS_FILE, users)
    save_artists(ARTISTS_FILE, artists)
    save_albums(ALBUMS_FILE, albums)
    save_collections(COLLECTIONS_FILE, collections)


def login(
    users: List[Dict],
    collections: List[Dict],
) -> Tuple[Dict, Dict]:
    """Войти в систему по имени; новый пользователь регистрируется."""
    name = input_text("Введите ваше имя: ")
    user = find_user_by_name(users, name)
    if user is None:
        user = add_user(users, name)
        print(f"Пользователь {user['name']} зарегистрирован.")
    else:
        print(f"С возвращением, {user['name']}!")
    collection = get_user_collection(collections, user["id"])
    if collection is None:
        collection = create_collection(collections, user["id"])
    return user, collection


def show_album_card(album: Dict, artists: List[Dict]) -> None:
    """Вывести подробную карточку альбома (сценарий из ПР1)."""
    artist = next(
        (a["name"] for a in artists if a["id"] == album["artist_id"]),
        "Неизвестный исполнитель",
    )
    rating = album["rating"]
    rating_text = (
        f"{rating}/{MAX_RATING}" if rating is not None else "нет оценки"
    )
    print(THIN_LINE)
    print(f" Название: {album['title']}")
    print(f" Исполнитель: {artist}")
    print(
        f" Год выпуска: {album['release_year']} "
        f"({get_album_age(album)} лет назад)"
    )
    print(f" Жанр: {album['genre']}")
    print(f" Песен: {album['songs_count']}")
    print(f" Оценка: {get_rating_stars(rating)} ({rating_text})")
    print(f" Статус: {get_album_status(album['is_listened'], rating)}")
    print()
    print("Рекомендация:")
    print(get_recommendation(album["genre"], rating))
    print(THIN_LINE)


def select_album(collection: Dict, albums: List[Dict]) -> Optional[Dict]:
    """Запросить идентификатор и найти альбом в коллекции."""
    album_id = input_int("ID альбома: ", min_value=1)
    album = find_album_by_id(albums, album_id)
    if album is None or album_id not in collection["album_ids"]:
        print("Альбом с таким ID не найден в вашей коллекции.")
        return None
    return album


def choose_artist(artists: List[Dict], genre: str) -> Dict:
    """Найти исполнителя по имени или создать нового."""
    name = input_text("Исполнитель: ")
    artist = find_artist_by_name(artists, name)
    if artist is None:
        country = input_text("Страна нового исполнителя: ")
        artist = add_artist(artists, name, country, genre)
        print(f"Добавлен новый исполнитель: {artist['name']}")
    return artist


def add_new_album(
    collection: Dict,
    albums: List[Dict],
    artists: List[Dict],
) -> None:
    """Пользовательский сценарий добавления альбома в коллекцию."""
    title = input_text("Название альбома: ")
    year = input_int(
        "Год выпуска: ",
        min_value=MIN_RELEASE_YEAR,
        max_value=date.today().year,
    )
    genre = input_text("Жанр: ")
    songs_count = input_int("Количество песен: ", min_value=0)
    artist = choose_artist(artists, genre)
    album = add_album_to_collection(
        collection, albums, title, artist["id"], year, genre, songs_count
    )
    if album is None:
        print("Такой альбом уже есть в вашей коллекции.")
        return
    print(f"Альбом добавлен (ID {album['id']}): «{album['title']}»")


def remove_album(collection: Dict, albums: List[Dict]) -> None:
    """Пользовательский сценарий удаления альбома из коллекции."""
    album = select_album(collection, albums)
    if album is None:
        return
    if remove_album_from_collection(collection, albums, album["id"]):
        print(f"Альбом «{album['title']}» удалён из коллекции.")


def rate_selected_album(collection: Dict, albums: List[Dict]) -> None:
    """Пользовательский сценарий оценки альбома."""
    album = select_album(collection, albums)
    if album is None:
        return
    rating = input_int(
        f"Оценка ({MIN_RATING}-{MAX_RATING}): ",
        min_value=MIN_RATING,
        max_value=MAX_RATING,
    )
    rate_album(album, rating)
    print(f"Оценка сохранена: {get_rating_stars(rating)}")


def listen_selected_album(collection: Dict, albums: List[Dict]) -> None:
    """Пользовательский сценарий отметки альбома прослушанным."""
    album = select_album(collection, albums)
    if album is None:
        return
    mark_album_listened(album)
    print(f"Альбом «{album['title']}» отмечен как прослушанный.")


def show_overview(collection_albums: List[Dict], artists: List[Dict]) -> None:
    """Статистика коллекции и последний добавленный альбом."""
    print(LINE)
    show_statistics(collection_albums)
    if collection_albums:
        print()
        print("Последний добавленный альбом:")
        show_album_card(collection_albums[-1], artists)


def sort_menu(collection_albums: List[Dict], artists: List[Dict]) -> None:
    """Вывод альбомов коллекции в выбранном порядке."""
    print("1. По оценке\n2. По году выпуска\n3. По названию")
    choice = input_int("Критерий: ", min_value=1, max_value=3)
    criteria = {1: "rating", 2: "year", 3: "title"}
    show_albums(sort_albums(collection_albums, criteria[choice]), artists)


def run_menu(
    collection: Dict,
    albums: List[Dict],
    artists: List[Dict],
) -> None:
    """Главный цикл меню приложения."""
    while True:
        print(MENU)
        choice = input_int("Выберите действие: ", 0, 12)
        my_albums = get_collection_albums(collection, albums)
        try:
            if choice == 0:
                return
            if choice == 1:
                show_albums(my_albums, artists)
            elif choice == 2:
                add_new_album(collection, albums, artists)
            elif choice == 3:
                remove_album(collection, albums)
            elif choice == 4:
                rate_selected_album(collection, albums)
            elif choice == 5:
                listen_selected_album(collection, albums)
            elif choice == 6:
                query = input_text("Название альбома или исполнитель: ")
                show_albums(find_album(my_albums, artists, query), artists)
            elif choice == 7:
                genre = input_text("Жанр: ")
                show_albums(filter_albums_by_genre(my_albums, genre), artists)
            elif choice == 8:
                sort_menu(my_albums, artists)
            elif choice == 9:
                album = select_album(collection, albums)
                if album is not None:
                    show_album_card(album, artists)
            elif choice == 10:
                show_overview(my_albums, artists)
            elif choice == 11:
                print(get_collection_recommendation(my_albums))
            elif choice == 12:
                show_artists(artists)
        except ValueError as error:
            print(f"Ошибка: {error}")


def main() -> None:
    """Точка входа: загрузка данных, меню, сохранение данных."""
    users, artists, albums, collections = load_data()
    print(LINE)
    print("СЕРВИС МУЗЫКАЛЬНЫХ КОЛЛЕКЦИЙ")
    print(LINE)
    try:
        _, collection = login(users, collections)
        run_menu(collection, albums, artists)
    except (KeyboardInterrupt, EOFError):
        print("\nЗавершение работы.")
    finally:
        save_data(users, artists, albums, collections)
    print(LINE)
    print("Music Collection Service v1.0")
    print(LINE)


if __name__ == "__main__":
    main()
