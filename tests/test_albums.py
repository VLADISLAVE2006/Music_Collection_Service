from datetime import date

import pytest

from models import Album, Artist, User
from models.albums import (
    filter_albums_by_genre,
    find_album,
    find_album_by_id,
    get_album_status,
    get_rating_stars,
    get_recommendation,
    sort_albums,
)


@pytest.fixture
def user():
    return User(1, "Алексей", date(2026, 9, 1))


@pytest.fixture
def artist():
    return Artist(1, "The Weeknd", "Канада", "Pop")


@pytest.fixture
def album(artist, user):
    return Album(1, "After Hours", artist, 2020, "Pop", user, 14)


def test_album_creation(album, artist, user):
    assert album.id == 1
    assert album.title == "After Hours"
    assert album.artist is artist
    assert album.user is user
    assert album.release_year == 2020
    assert album.rating is None
    assert not album.is_listened


def test_album_str(album):
    assert str(album) == (
        "After Hours — The Weeknd (2020), Pop, ☆☆☆☆☆, не прослушан"
    )


def test_album_age(album):
    assert album.age() == date.today().year - 2020


def test_album_empty_title_forbidden(artist, user):
    with pytest.raises(ValueError):
        Album(1, "  ", artist, 2020, "Pop", user)


def test_album_future_year_forbidden(artist, user):
    with pytest.raises(ValueError):
        Album(1, "Future", artist, date.today().year + 1, "Pop", user)


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_album_invalid_rating_forbidden(artist, user, rating):
    with pytest.raises(ValueError):
        Album(1, "Test", artist, 2020, "Pop", user, rating=rating)


def test_album_rate(album):
    album.rate(5)
    assert album.rating == 5
    assert album.is_listened


def test_album_rate_invalid(album):
    with pytest.raises(ValueError):
        album.rate(7)
    assert album.rating is None


def test_album_mark_listened(album):
    album.mark_listened()
    assert album.is_listened


def test_validate_rating_static():
    assert Album.validate_rating(1)
    assert Album.validate_rating(5)
    assert not Album.validate_rating(6)


def test_rating_stars():
    assert get_rating_stars(4) == "★★★★☆"
    assert get_rating_stars(None) == "☆☆☆☆☆"


def test_album_status(album):
    assert get_album_status(album) == "Еще не прослушан"
    album.mark_listened()
    assert get_album_status(album) == "Прослушан, но не оценён"
    album.rate(5)
    assert get_album_status(album) == "Отличный альбом! Рекомендую!"
    album.rate(3)
    assert get_album_status(album) == "Хороший альбом, стоит послушать"
    album.rate(2)
    assert get_album_status(album) == "Прослушан, но не впечатлил"


def test_album_recommendation(album):
    assert "Оцените" in get_recommendation(album)
    album.rate(5)
    assert "Если вам нравится Pop" in get_recommendation(album)
    album.rate(1)
    assert "другие жанры" in get_recommendation(album)


@pytest.fixture
def albums(artist, user):
    return [
        Album(1, "After Hours", artist, 2020, "Pop", user, rating=5),
        Album(2, "Discovery", Artist(2, "Daft Punk", "Франция", "Electronic"),
              2001, "Electronic", user, rating=3),
        Album(3, "Homework", Artist(2, "Daft Punk", "Франция", "Electronic"),
              1997, "Electronic", user),
    ]


def test_find_album(albums):
    assert [a.id for a in find_album(albums, "daft")] == [2, 3]
    assert [a.id for a in find_album(albums, "after")] == [1]
    assert find_album(albums, "zzz") == []


def test_find_album_by_id(albums):
    assert find_album_by_id(albums, 2) is albums[1]
    assert find_album_by_id(albums, 99) is None


def test_filter_albums_by_genre(albums):
    result = filter_albums_by_genre(albums, "electronic")
    assert [a.id for a in result] == [2, 3]


def test_sort_albums(albums):
    assert [a.id for a in sort_albums(albums, "rating")] == [1, 2, 3]
    assert [a.id for a in sort_albums(albums, "year")] == [3, 2, 1]
    assert [a.id for a in sort_albums(albums, "title")] == [1, 2, 3]
    with pytest.raises(ValueError):
        sort_albums(albums, "unknown")


def test_rating_stars_property(album):
    assert album.rating_stars == "☆☆☆☆☆"
    album.rate(4)
    assert album.rating_stars == "★★★★☆"
