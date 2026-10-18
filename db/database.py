"""Подключение к базе данных SQLite проекта Maestro."""
import sqlite3
from pathlib import Path
from typing import Optional, Union

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "maestro.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

PathLike = Union[str, Path]


def get_connection(path: Optional[PathLike] = None) -> sqlite3.Connection:
    """Создать соединение с базой данных и включить внешние ключи.

    По умолчанию SQLite не проверяет внешние ключи, поэтому
    PRAGMA foreign_keys = ON выполняется для каждого нового соединения.
    """
    conn = sqlite3.connect(path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы из файла sql/schema.sql (повторный запуск безопасен)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
