from datetime import date

from models import Album, Artist, Collection, User
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


def make_data():
    user = User(1, "Алексей", date(2026, 9, 1))
    artist = Artist(1, "The Weeknd", "Канада", "Pop")
    album = Album(1, "After Hours", artist, 2020, "Pop", user, 14, 5, True)
    collection = Collection(1, user)
    collection.add_album(album)
    return user, artist, album, collection


def test_users_roundtrip(tmp_path):
    user, _, _, _ = make_data()
    path = tmp_path / "users.json"
    save_users(path, [user])
    loaded = load_users(path)
    assert len(loaded) == 1
    assert loaded[0].name == "Алексей"
    assert loaded[0].registered_at == date(2026, 9, 1)


def test_artists_roundtrip(tmp_path):
    _, artist, _, _ = make_data()
    path = tmp_path / "artists.json"
    save_artists(path, [artist])
    loaded = load_artists(path)
    assert loaded[0].name == "The Weeknd"
    assert loaded[0].country == "Канада"


def test_albums_restore_links(tmp_path):
    user, artist, album, _ = make_data()
    path = tmp_path / "albums.json"
    save_albums(path, [album])
    loaded = load_albums(path, [artist], [user])
    assert len(loaded) == 1
    assert loaded[0].artist is artist
    assert loaded[0].user is user
    assert loaded[0].rating == 5
    assert loaded[0].is_listened


def test_album_without_artist_is_skipped(tmp_path):
    user, _, album, _ = make_data()
    path = tmp_path / "albums.json"
    save_albums(path, [album])
    assert load_albums(path, [], [user]) == []


def test_collections_restore_links(tmp_path):
    user, _, album, collection = make_data()
    path = tmp_path / "collections.json"
    save_collections(path, [collection])
    loaded = load_collections(path, [user], [album])
    assert loaded[0].user is user
    assert loaded[0].albums == [album]


def test_json_stores_ids_not_objects(tmp_path):
    _, _, album, _ = make_data()
    path = tmp_path / "albums.json"
    save_albums(path, [album])
    text = path.read_text(encoding="utf-8")
    assert '"artist_id": 1' in text
    assert '"user_id": 1' in text


def test_missing_file_returns_empty_list(tmp_path):
    assert load_users(tmp_path / "missing.json") == []


def test_broken_json_returns_empty_list(tmp_path):
    path = tmp_path / "users.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_users(path) == []
