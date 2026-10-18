import ast
import re
import sqlite3
from typing import Dict

import pytest

from db import database
from db.database import BASE_DIR, get_connection
from db.import_json import DATA_DIR, import_all, load_json

QUERIES_FILE = BASE_DIR / "sql" / "queries.sql"
CODE_FILES = [
    BASE_DIR / "albums" / "views.py",
    BASE_DIR / "artists" / "views.py",
    BASE_DIR / "library" / "views.py",
    BASE_DIR / "db" / "database.py",
    BASE_DIR / "db" / "import_json.py",
]
VIEW_FILES = CODE_FILES[:3]

# Значения параметров ? для запросов, которые их используют
PARAMS = {
    4: [1],
    6: [1],
    7: [1],
    9: [1],
    10: [1],
    11: [1],
    12: [1],
    13: ["", "", 0, ""],
}


def normalize(sql: str) -> str:
    """Привести SQL к виду без лишних пробелов и завершающей «;»."""
    return " ".join(sql.split()).rstrip(";").strip()


def load_queries() -> Dict[int, str]:
    """Прочитать sql/queries.sql: номер запроса -> текст без комментариев."""
    text = QUERIES_FILE.read_text(encoding="utf-8")
    parts = re.split(r"^-- Запрос (\d+)\.[^\n]*\n", text, flags=re.M)
    queries = {}
    for number, body in zip(parts[1::2], parts[2::2]):
        lines = [x for x in body.splitlines() if not x.startswith("--")]
        queries[int(number)] = normalize("\n".join(lines))
    return queries


def view_queries():
    """Найти в представлениях строки-SQL (ast, без выполнения кода)."""
    found = []
    for path in VIEW_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.value.lstrip().upper().startswith("SELECT")
            ):
                found.append((path.name, normalize(node.value)))
    return found


@pytest.fixture
def conn(tmp_path):
    connection = get_connection(tmp_path / "test.sqlite")
    import_all(connection)
    connection.commit()
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


COUNT_SQL = {
    "users": "SELECT COUNT(*) FROM users",
    "artists": "SELECT COUNT(*) FROM artists",
    "albums": "SELECT COUNT(*) FROM albums",
    "collections": "SELECT COUNT(*) FROM collections",
    "collection_albums": "SELECT COUNT(*) FROM collection_albums",
}

FOREIGN_KEYS_SQL = {
    "albums": "PRAGMA foreign_key_list(albums)",
    "collections": "PRAGMA foreign_key_list(collections)",
    "collection_albums": "PRAGMA foreign_key_list(collection_albums)",
}


def count(conn, table):
    return conn.execute(COUNT_SQL[table]).fetchone()[0]


def test_schema_creates_all_tables(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    assert {row["name"] for row in rows} == {
        "users", "artists", "albums", "collections", "collection_albums",
    }


@pytest.mark.parametrize("table, targets", [
    ("albums", {"artists", "users"}),
    ("collections", {"users"}),
    ("collection_albums", {"collections", "albums"}),
])
def test_foreign_keys_are_defined(conn, table, targets):
    rows = conn.execute(FOREIGN_KEYS_SQL[table]).fetchall()
    assert {row["table"] for row in rows} == targets


def test_connection_enables_foreign_keys(tmp_path):
    connection = get_connection(tmp_path / "fk.sqlite")
    try:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


def test_foreign_key_violation_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO albums (id, title, artist_id, release_year, genre,"
            " user_id) VALUES (99, 'X', 999, 2020, 'Pop', 1)"
        )


def test_rating_check_constraint(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE albums SET rating = 9 WHERE id = 1")


def test_import_counts_match_json(conn):
    for table in ("users", "artists", "albums", "collections"):
        assert count(conn, table) == len(
            load_json(DATA_DIR / f"{table}.json")
        )
    collections = load_json(DATA_DIR / "collections.json")
    expected = sum(len(item["album_ids"]) for item in collections)
    assert count(conn, "collection_albums") == expected


def test_import_is_repeatable(conn):
    before = count(conn, "albums")
    import_all(conn)
    conn.commit()
    assert count(conn, "albums") == before
    assert count(conn, "collection_albums") > 0


def test_null_rating_and_bool_are_imported_correctly(conn):
    albums = load_json(DATA_DIR / "albums.json")
    without_rating = sum(1 for item in albums if item["rating"] is None)
    row = conn.execute(
        "SELECT COUNT(*) AS total, COUNT(rating) AS rated FROM albums"
    ).fetchone()
    assert row["total"] - row["rated"] == without_rating
    listened = conn.execute(
        "SELECT COUNT(*) FROM albums WHERE is_listened = 1"
    ).fetchone()[0]
    assert listened == sum(1 for item in albums if item["is_listened"])


def test_queries_file_has_required_volume_and_kinds():
    queries = load_queries()
    assert len(queries) >= 10
    texts = list(queries.values())

    def with_word(pattern):
        return sum(1 for text in texts if re.search(pattern, text, re.I))

    assert with_word(r"\bWHERE\b") >= 2
    assert with_word(r"\bJOIN\b") >= 2
    assert with_word(r"\b(COUNT|AVG|SUM)\(") >= 2
    assert with_word(r"\bGROUP BY\b") >= 2
    assert with_word(r"\bHAVING\b") >= 1
    plain = [t for t in texts if not re.search(r"WHERE|JOIN|GROUP", t)]
    assert len(plain) >= 2


def test_every_query_runs(conn):
    for number, sql in load_queries().items():
        conn.execute(sql, PARAMS.get(number, [])).fetchall()


def test_query_results_match_json_data(conn):
    queries = load_queries()
    albums = load_json(DATA_DIR / "albums.json")

    listing = conn.execute(queries[3]).fetchall()
    assert len(listing) == len(albums)
    titles = [row["title"] for row in listing]
    assert titles == sorted(titles)

    stats = conn.execute(queries[11], [1]).fetchone()
    ids = load_json(DATA_DIR / "collections.json")[0]["album_ids"]
    chosen = [a for a in albums if a["id"] in ids]
    assert stats["total_albums"] == len(chosen)
    assert stats["total_songs"] == sum(a["songs_count"] for a in chosen)
    ratings = [a["rating"] for a in chosen if a["rating"] is not None]
    assert stats["average_rating"] == pytest.approx(
        sum(ratings) / len(ratings)
    )

    assert [r["artist_name"] for r in conn.execute(queries[16])] == [
        "Daft Punk"
    ]
    assert conn.execute(queries[19]).fetchall() == []
    unrated = [a["title"] for a in albums if a["rating"] is None]
    assert [r["title"] for r in conn.execute(queries[18])] == unrated
    by_genre = conn.execute(queries[15]).fetchall()
    assert sum(r["albums_count"] for r in by_genre) == len(albums)


def test_views_use_the_same_sql_as_queries_file():
    saved = set(load_queries().values())
    in_views = view_queries()
    assert len(in_views) >= 10
    missing = [name for name, sql in in_views if sql not in saved]
    assert missing == []


def test_search_query_is_parameterized_and_safe(conn):
    sql = load_queries()[13]
    attack = "x' OR '1'='1"
    assert conn.execute(sql, [attack, attack, 0, ""]).fetchall() == []
    assert count(conn, "albums") > 0
    found = conn.execute(sql, ["Electronic", "Electronic", 0, ""]).fetchall()
    assert {row["genre"] for row in found} == {"Electronic"}


def test_sql_is_not_built_with_f_strings():
    pattern = re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\b")
    offenders = []
    for path in CODE_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                text = "".join(
                    part.value for part in node.values
                    if isinstance(part, ast.Constant)
                )
                if pattern.search(text):
                    offenders.append((path.name, text))
    assert offenders == []


def test_default_database_path_is_inside_data_directory():
    assert database.DB_PATH.parent == BASE_DIR / "data"
