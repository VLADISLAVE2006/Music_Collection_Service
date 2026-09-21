"""Загрузка и сохранение данных в JSON-файлах.

Чтение и запись выполняются через контекстный менеджер with,
ошибки файлов обрабатываются исключениями.
"""
import json
from pathlib import Path
from typing import Dict, List, Union

PathLike = Union[str, Path]

USER_KEYS = ("id", "name", "registered_at")
ARTIST_KEYS = ("id", "name", "country", "genre")
ALBUM_KEYS = (
    "id", "title", "artist_id", "release_year", "genre",
    "songs_count", "rating", "is_listened", "user_id",
)
COLLECTION_KEYS = ("id", "user_id", "album_ids")


def _read_json(filename: PathLike, required_keys: tuple) -> List[Dict]:
    """Прочитать список записей из JSON-файла.

    Если файла нет или он повреждён, выводится сообщение и возвращается
    пустой список. Записи без обязательных ключей пропускаются.
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
    records = []
    for item in data:
        if isinstance(item, dict) and all(k in item for k in required_keys):
            records.append(item)
        else:
            print(f"Пропущена некорректная запись в файле {filename}.")
    return records


def _write_json(filename: PathLike, data: List[Dict]) -> None:
    """Записать список записей в JSON-файл."""
    try:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Не удалось сохранить файл {filename}: {error}")


def load_users(filename: PathLike) -> List[Dict]:
    """Загрузить пользователей из JSON-файла."""
    return _read_json(filename, USER_KEYS)


def save_users(filename: PathLike, users: List[Dict]) -> None:
    """Сохранить пользователей в JSON-файл."""
    _write_json(filename, users)


def load_artists(filename: PathLike) -> List[Dict]:
    """Загрузить исполнителей из JSON-файла."""
    return _read_json(filename, ARTIST_KEYS)


def save_artists(filename: PathLike, artists: List[Dict]) -> None:
    """Сохранить исполнителей в JSON-файл."""
    _write_json(filename, artists)


def load_albums(filename: PathLike) -> List[Dict]:
    """Загрузить альбомы из JSON-файла."""
    return _read_json(filename, ALBUM_KEYS)


def save_albums(filename: PathLike, albums: List[Dict]) -> None:
    """Сохранить альбомы в JSON-файл."""
    _write_json(filename, albums)


def load_collections(filename: PathLike) -> List[Dict]:
    """Загрузить коллекции из JSON-файла."""
    return _read_json(filename, COLLECTION_KEYS)


def save_collections(filename: PathLike, collections: List[Dict]) -> None:
    """Сохранить коллекции в JSON-файл."""
    _write_json(filename, collections)
