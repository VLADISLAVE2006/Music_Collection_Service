import pytest

from models import Artist
from models.artists import (
    add_artist,
    find_artist,
    find_artist_by_id,
    find_artist_by_name,
)


def test_artist_creation():
    artist = Artist(1, "The Weeknd", "Канада", "Pop")
    assert artist.id == 1
    assert artist.name == "The Weeknd"
    assert artist.country == "Канада"
    assert artist.genre == "Pop"


def test_artist_str():
    artist = Artist(1, "The Weeknd", "Канада", "Pop")
    assert str(artist) == "The Weeknd (Канада), жанр: Pop"


def test_artist_empty_name_forbidden():
    with pytest.raises(ValueError):
        Artist(1, "   ", "Канада", "Pop")


def test_artist_from_data():
    data = {"id": 2, "name": "Daft Punk", "country": "Франция",
            "genre": "Electronic"}
    artist = Artist.from_data(data)
    assert artist.id == 2
    assert artist.name == "Daft Punk"


def test_add_and_find_artist():
    artists = []
    artist = add_artist(artists, "Radiohead", "Великобритания", "Rock")
    assert artists == [artist]
    assert artist.id == 1
    assert find_artist(artists, "radio") == [artist]
    assert find_artist(artists, "abba") == []
    assert find_artist_by_id(artists, 1) is artist
    assert find_artist_by_id(artists, 99) is None
    assert find_artist_by_name(artists, "RADIOHEAD") is artist
