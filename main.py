from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

from models import Album, Artist, Collection, User
from models.albums import (
    MAX_RATING,
    MIN_RATING,
    MIN_RELEASE_YEAR,
    filter_albums_by_genre,
    find_album,
    find_album_by_id,
    get_album_status,
    get_rating_stars,
    get_recommendation,
    show_albums,
    sort_albums,
)
from models.artists import (
    add_artist,
    find_artist_by_name,
    show_artists,
)
from models.collection import (
    add_album_to_collection,
    create_collection,
    get_collection_recommendation,
    get_user_collection,
    remove_album_from_collection,
    show_statistics,
)
from models.users import add_user, find_user_by_name
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

AppData = Tuple[List[User], List[Artist], List[Album], List[Collection]]


def load_data() -> AppData:
    """Загрузить все данные из JSON-файлов и восстановить связи."""
    users = load_users(USERS_FILE)
    artists = load_artists(ARTISTS_FILE)
    albums = load_albums(ALBUMS_FILE, artists, users)
    collections = load_collections(COLLECTIONS_FILE, users, albums)
    return users, artists, albums, collections


def save_data(
    users: List[User],
    artists: List[Artist],
    albums: List[Album],
    collections: List[Collection],
) -> None:
    """Сохранить все данные в JSON-файлы."""
    save_users(USERS_FILE, users)
    save_artists(ARTISTS_FILE, artists)
    save_albums(ALBUMS_FILE, albums)
    save_collections(COLLECTIONS_FILE, collections)


def print_header(collection: Collection) -> None:
    """Вывести заголовок приложения."""
    print(LINE)
    print(f"МУЗЫКАЛЬНАЯ КОЛЛЕКЦИЯ: {collection.user.name}".upper())
    print(LINE)


def login(
    users: List[User],
    collections: List[Collection],
) -> Tuple[User, Collection]:
    """Войти в систему по имени; новый пользователь регистрируется."""
    name = input_text("Введите ваше имя: ")
    user = find_user_by_name(users, name)
    if user is None:
        user = add_user(users, name)
        print(f"Пользователь {user.name} зарегистрирован.")
    else:
        print(f"С возвращением, {user.name}!")
    collection = get_user_collection(collections, user)
    if collection is None:
        collection = create_collection(collections, user)
    return user, collection


def show_album_card(album: Album) -> None:
    """Вывести подробную карточку альбома (сценарий из ПР1)."""
    rating_text = (
        f"{album.rating}/{MAX_RATING}" if album.rating is not None
        else "нет оценки"
    )
    print(THIN_LINE)
    print(f" Название: {album.title}")
    print(f" Исполнитель: {album.artist.name}")
    print(f" Год выпуска: {album.release_year} ({album.age()} лет назад)")
    print(f" Жанр: {album.genre}")
    print(f" Песен: {album.songs_count}")
    print(f" Оценка: {get_rating_stars(album.rating)} ({rating_text})")
    print(f" Статус: {get_album_status(album)}")
    print()
    print("Рекомендация:")
    print(get_recommendation(album))
    print(THIN_LINE)


def select_album(collection: Collection) -> Optional[Album]:
    """Запросить идентификатор и найти альбом в коллекции."""
    album_id = input_int("ID альбома: ", min_value=1)
    album = find_album_by_id(collection.albums, album_id)
    if album is None:
        print("Альбом с таким ID не найден в вашей коллекции.")
    return album


def choose_artist(artists: List[Artist], genre: str) -> Artist:
    """Найти исполнителя по имени или создать нового."""
    name = input_text("Исполнитель: ")
    artist = find_artist_by_name(artists, name)
    if artist is None:
        country = input_text("Страна нового исполнителя: ")
        artist = add_artist(artists, name, country, genre)
        print(f"Добавлен новый исполнитель: {artist.name}")
    return artist


def add_new_album(
    collection: Collection,
    albums: List[Album],
    artists: List[Artist],
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
        collection, albums, title, artist, year, genre, songs_count
    )
    if album is None:
        print("Такой альбом уже есть в вашей коллекции.")
        return
    print(f"Альбом добавлен (ID {album.id}): {album}")


def remove_album(collection: Collection, albums: List[Album]) -> None:
    """Пользовательский сценарий удаления альбома из коллекции."""
    album = select_album(collection)
    if album is None:
        return
    if remove_album_from_collection(collection, albums, album.id):
        print(f"Альбом «{album.title}» удалён из коллекции.")


def rate_album(collection: Collection) -> None:
    """Пользовательский сценарий оценки альбома."""
    album = select_album(collection)
    if album is None:
        return
    rating = input_int(
        f"Оценка ({MIN_RATING}-{MAX_RATING}): ",
        min_value=MIN_RATING,
        max_value=MAX_RATING,
    )
    album.rate(rating)
    print(f"Оценка сохранена: {get_rating_stars(album.rating)}")


def mark_album_listened(collection: Collection) -> None:
    """Пользовательский сценарий отметки альбома прослушанным."""
    album = select_album(collection)
    if album is None:
        return
    album.mark_listened()
    print(f"Альбом «{album.title}» отмечен как прослушанный.")


def search_albums(collection: Collection) -> None:
    """Поиск альбомов коллекции по названию или исполнителю."""
    query = input_text("Название альбома или исполнитель: ")
    show_albums(find_album(collection.albums, query))


def show_genre_albums(collection: Collection) -> None:
    """Вывод альбомов коллекции выбранного жанра."""
    genre = input_text("Жанр: ")
    show_albums(filter_albums_by_genre(collection.albums, genre))


def show_sorted_albums(collection: Collection) -> None:
    """Вывод альбомов коллекции в выбранном порядке."""
    print("1. По оценке\n2. По году выпуска\n3. По названию")
    choice = input_int("Критерий: ", min_value=1, max_value=3)
    criteria = {1: "rating", 2: "year", 3: "title"}
    show_albums(sort_albums(collection.albums, criteria[choice]))


def show_overview(collection: Collection) -> None:
    """Статистика коллекции и последний добавленный альбом."""
    print(LINE)
    print(collection.user.name.upper())
    print(LINE)
    show_statistics(collection)
    if collection.albums:
        print()
        print("Последний добавленный альбом:")
        show_album_card(collection.albums[-1])


def show_card(collection: Collection) -> None:
    """Вывод карточки выбранного альбома."""
    album = select_album(collection)
    if album is not None:
        show_album_card(album)


def run_menu(
    collection: Collection,
    albums: List[Album],
    artists: List[Artist],
) -> None:
    """Главный цикл меню приложения."""
    while True:
        print(MENU)
        choice = input_int("Выберите действие: ", 0, 12)
        try:
            if choice == 0:
                return
            if choice == 1:
                show_albums(collection.albums)
            elif choice == 2:
                add_new_album(collection, albums, artists)
            elif choice == 3:
                remove_album(collection, albums)
            elif choice == 4:
                rate_album(collection)
            elif choice == 5:
                mark_album_listened(collection)
            elif choice == 6:
                search_albums(collection)
            elif choice == 7:
                show_genre_albums(collection)
            elif choice == 8:
                show_sorted_albums(collection)
            elif choice == 9:
                show_card(collection)
            elif choice == 10:
                show_overview(collection)
            elif choice == 11:
                print(get_collection_recommendation(collection))
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
        print_header(collection)
        run_menu(collection, albums, artists)
    except (KeyboardInterrupt, EOFError):
        print("\nЗавершение работы.")
    finally:
        save_data(users, artists, albums, collections)
    print(LINE)
    print("Music Collection Service v2.0")
    print(LINE)


if __name__ == "__main__":
    main()
