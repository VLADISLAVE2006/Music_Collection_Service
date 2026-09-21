import json

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


def test_users_roundtrip(tmp_path):
    users = [{"id": 1, "name": "Владислав", "registered_at": "2026-09-01"}]
    path = tmp_path / "users.json"
    save_users(path, users)
    assert load_users(path) == users


def test_artists_roundtrip(tmp_path):
    artists = [{"id": 1, "name": "The Weeknd", "country": "Канада",
                "genre": "Pop"}]
    path = tmp_path / "artists.json"
    save_artists(path, artists)
    assert load_artists(path) == artists


def test_albums_roundtrip(tmp_path):
    albums = [{
        "id": 1, "title": "After Hours", "artist_id": 1,
        "release_year": 2020, "genre": "Pop", "songs_count": 14,
        "rating": 5, "is_listened": True, "user_id": 1,
    }]
    path = tmp_path / "albums.json"
    save_albums(path, albums)
    assert load_albums(path) == albums


def test_collections_roundtrip(tmp_path):
    collections = [{"id": 1, "user_id": 1, "album_ids": [1, 2]}]
    path = tmp_path / "collections.json"
    save_collections(path, collections)
    assert load_collections(path) == collections


def test_missing_file_returns_empty_list(tmp_path):
    assert load_users(tmp_path / "missing.json") == []


def test_broken_json_returns_empty_list(tmp_path):
    path = tmp_path / "users.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_users(path) == []


def test_record_without_required_keys_is_skipped(tmp_path):
    path = tmp_path / "users.json"
    data = [{"id": 1, "name": "Владислав", "registered_at": "2026-09-01"},
            {"id": 2}]
    path.write_text(json.dumps(data), encoding="utf-8")
    assert len(load_users(path)) == 1
