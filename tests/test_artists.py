import pytest

from artists import (
    add_artist,
    find_artist,
    find_artist_by_id,
    find_artist_by_name,
    get_artist_name,
)


def test_add_artist():
    artists = []
    artist = add_artist(artists, "The Weeknd", "Канада", "Pop")
    assert artists == [artist]
    assert artist == {
        "id": 1, "name": "The Weeknd", "country": "Канада", "genre": "Pop",
    }


def test_add_artist_generates_unique_ids():
    artists = []
    add_artist(artists, "The Weeknd", "Канада", "Pop")
    second = add_artist(artists, "Daft Punk", "Франция", "Electronic")
    assert second["id"] == 2


def test_add_artist_empty_name_forbidden():
    with pytest.raises(ValueError):
        add_artist([], "   ", "Канада", "Pop")


def test_find_artist():
    artists = []
    artist = add_artist(artists, "Radiohead", "Великобритания", "Rock")
    assert find_artist(artists, "radio") == [artist]
    assert find_artist(artists, "abba") == []


def test_find_artist_by_id_and_name():
    artists = []
    artist = add_artist(artists, "Radiohead", "Великобритания", "Rock")
    assert find_artist_by_id(artists, 1) is artist
    assert find_artist_by_id(artists, 99) is None
    assert find_artist_by_name(artists, "RADIOHEAD") is artist
    assert get_artist_name(artists, 1) == "Radiohead"
    assert get_artist_name(artists, 99) == "Неизвестный исполнитель"
