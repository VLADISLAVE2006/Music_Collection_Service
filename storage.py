"""Загрузка и сохранение данных в JSON-файлах.

В JSON хранятся только простые данные; связи между объектами
записываются идентификаторами (artist_id, user_id, album_ids).
"""
import json
from pathlib import Path
from typing import List, Union

from models import Album, Artist, Collection, User
from models.albums import find_album_by_id
from models.artists import find_artist_by_id
from models.users import find_user_by_id

PathLike = Union[str, Path]


def _read_json(filename: PathLike) -> List[dict]:
    """Прочитать список записей из JSON-файла.

    Если файла нет или он повреждён, выводится сообщение
    и возвращается пустой список.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, он будет создан при сохранении.")
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} содержит некорректный JSON, он пропущен.")
        return []
    except OSError as error:
        print(f"Не удалось прочитать файл {filename}: {error}")
        return []
    if not isinstance(data, list):
        print(f"Файл {filename} должен содержать список, он пропущен.")
        return []
    return data


def _write_json(filename: PathLike, data: List[dict]) -> None:
    """Записать список записей в JSON-файл."""
    try:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Не удалось сохранить файл {filename}: {error}")


def _skip_message(entity: str, error: Exception) -> None:
    """Вывести сообщение о пропущенной некорректной записи."""
    print(f"Пропущена некорректная запись ({entity}): {error!r}")


def load_users(filename: PathLike) -> List[User]:
    """Загрузить пользователей из JSON в объекты User."""
    users: List[User] = []
    for item in _read_json(filename):
        try:
            users.append(User.from_data(item))
        except (KeyError, TypeError, ValueError) as error:
            _skip_message("пользователь", error)
    return users


def save_users(filename: PathLike, users: List[User]) -> None:
    """Сохранить объекты User в JSON."""
    _write_json(filename, [
        {
            "id": user.id,
            "name": user.name,
            "registered_at": user.registered_at.isoformat(),
        }
        for user in users
    ])


def load_artists(filename: PathLike) -> List[Artist]:
    """Загрузить исполнителей из JSON в объекты Artist."""
    artists: List[Artist] = []
    for item in _read_json(filename):
        try:
            artists.append(Artist.from_data(item))
        except (KeyError, TypeError, ValueError) as error:
            _skip_message("исполнитель", error)
    return artists


def save_artists(filename: PathLike, artists: List[Artist]) -> None:
    """Сохранить объекты Artist в JSON."""
    _write_json(filename, [
        {
            "id": artist.id,
            "name": artist.name,
            "country": artist.country,
            "genre": artist.genre,
        }
        for artist in artists
    ])


def load_albums(
    filename: PathLike,
    artists: List[Artist],
    users: List[User],
) -> List[Album]:
    """Загрузить альбомы из JSON, восстановив связи с Artist и User.

    Альбом, для которого не найден исполнитель или пользователь,
    не создаётся как корректный объект.
    """
    albums: List[Album] = []
    for item in _read_json(filename):
        try:
            artist = find_artist_by_id(artists, item["artist_id"])
            user = find_user_by_id(users, item["user_id"])
            if artist is None or user is None:
                print(
                    f"Альбом id={item['id']} пропущен: "
                    "не найден исполнитель или пользователь."
                )
                continue
            albums.append(Album(
                album_id=item["id"],
                title=item["title"],
                artist=artist,
                release_year=item["release_year"],
                genre=item["genre"],
                user=user,
                songs_count=item["songs_count"],
                rating=item["rating"],
                is_listened=item["is_listened"],
            ))
        except (KeyError, TypeError, ValueError) as error:
            _skip_message("альбом", error)
    return albums


def save_albums(filename: PathLike, albums: List[Album]) -> None:
    """Сохранить объекты Album в JSON (связи — через идентификаторы)."""
    _write_json(filename, [
        {
            "id": album.id,
            "title": album.title,
            "artist_id": album.artist.id,
            "release_year": album.release_year,
            "genre": album.genre,
            "songs_count": album.songs_count,
            "rating": album.rating,
            "is_listened": album.is_listened,
            "user_id": album.user.id,
        }
        for album in albums
    ])


def load_collections(
    filename: PathLike,
    users: List[User],
    albums: List[Album],
) -> List[Collection]:
    """Загрузить коллекции из JSON, восстановив связи с User и Album."""
    collections: List[Collection] = []
    for item in _read_json(filename):
        try:
            user = find_user_by_id(users, item["user_id"])
            if user is None:
                print(
                    f"Коллекция id={item['id']} пропущена: "
                    "не найден пользователь."
                )
                continue
            collection = Collection(item["id"], user)
            for album_id in item["album_ids"]:
                album = find_album_by_id(albums, album_id)
                if album is None:
                    print(f"Альбом id={album_id} не найден, пропущен.")
                    continue
                collection.add_album(album)
            collections.append(collection)
        except (KeyError, TypeError, ValueError) as error:
            _skip_message("коллекция", error)
    return collections


def save_collections(
    filename: PathLike,
    collections: List[Collection],
) -> None:
    """Сохранить объекты Collection в JSON (альбомы — по идентификаторам)."""
    _write_json(filename, [
        {
            "id": collection.id,
            "user_id": collection.user.id,
            "album_ids": [album.id for album in collection.albums],
        }
        for collection in collections
    ])
