"""Перенос данных проекта из JSON-файлов в таблицы SQLite.

Запуск из корня проекта: python -m db.import_json
"""
import json
import sqlite3
from pathlib import Path
from typing import List

from db.database import BASE_DIR, create_schema, get_connection

DATA_DIR = BASE_DIR / "data"

# Порядок очистки: сначала таблицы со ссылками, затем родительские
CLEAR_STATEMENTS = (
    "DELETE FROM collection_albums",
    "DELETE FROM collections",
    "DELETE FROM albums",
    "DELETE FROM artists",
    "DELETE FROM users",
)

COUNT_QUERIES = {
    "users": "SELECT COUNT(*) FROM users",
    "artists": "SELECT COUNT(*) FROM artists",
    "albums": "SELECT COUNT(*) FROM albums",
    "collections": "SELECT COUNT(*) FROM collections",
    "collection_albums": "SELECT COUNT(*) FROM collection_albums",
}


def load_json(filename: Path) -> List[dict]:
    """Прочитать список записей из JSON-файла."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def clear_tables(conn: sqlite3.Connection) -> None:
    """Удалить старые записи, чтобы импорт можно было запускать повторно."""
    for statement in CLEAR_STATEMENTS:
        conn.execute(statement)


def import_users(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Перенести пользователей."""
    users = load_json(data_dir / "users.json")
    conn.executemany(
        """
        INSERT INTO users (id, name, registered_at)
        VALUES (?, ?, ?)
        """,
        [
            (user["id"], user["name"], user["registered_at"])
            for user in users
        ],
    )


def import_artists(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Перенести исполнителей."""
    artists = load_json(data_dir / "artists.json")
    conn.executemany(
        """
        INSERT INTO artists (id, name, country, genre)
        VALUES (?, ?, ?, ?)
        """,
        [
            (a["id"], a["name"], a["country"], a["genre"])
            for a in artists
        ],
    )


def import_albums(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Перенести альбомы (логические значения хранятся как 0 и 1)."""
    albums = load_json(data_dir / "albums.json")
    conn.executemany(
        """
        INSERT INTO albums (
            id, title, artist_id, release_year, genre,
            songs_count, rating, is_listened, user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                album["id"],
                album["title"],
                album["artist_id"],
                album["release_year"],
                album["genre"],
                album["songs_count"],
                album["rating"],
                int(album["is_listened"]),
                album["user_id"],
            )
            for album in albums
        ],
    )


def import_collections(conn: sqlite3.Connection, data_dir: Path) -> None:
    """Перенести коллекции и их состав (связь с альбомами)."""
    collections = load_json(data_dir / "collections.json")
    conn.executemany(
        "INSERT INTO collections (id, user_id) VALUES (?, ?)",
        [(item["id"], item["user_id"]) for item in collections],
    )
    conn.executemany(
        """
        INSERT INTO collection_albums (collection_id, album_id)
        VALUES (?, ?)
        """,
        [
            (item["id"], album_id)
            for item in collections
            for album_id in item["album_ids"]
        ],
    )


def import_all(conn: sqlite3.Connection, data_dir: Path = DATA_DIR) -> None:
    """Создать схему и перенести все данные (родительские таблицы первыми).

    Внешние ключи проверяются, поэтому альбом нельзя вставить раньше
    исполнителя и пользователя, а состав коллекции раньше альбомов.
    """
    create_schema(conn)
    clear_tables(conn)
    import_users(conn, data_dir)
    import_artists(conn, data_dir)
    import_albums(conn, data_dir)
    import_collections(conn, data_dir)


def main() -> None:
    """Выполнить импорт; при ошибке откатить все изменения."""
    conn = get_connection()
    try:
        import_all(conn)
        conn.commit()
        for table, query in COUNT_QUERIES.items():
            print(f"{table}: {conn.execute(query).fetchone()[0]}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
