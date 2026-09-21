from datetime import date

import pytest

from albums import (
    create_album,
    filter_albums_by_genre,
    find_album,
    find_album_by_id,
    format_album,
    get_album_age,
    get_album_status,
    get_rating_stars,
    get_recommendation,
    mark_album_listened,
    rate_album,
    sort_albums,
    validate_rating,
    validate_year,
)

ARTISTS = [
    {"id": 1, "name": "The Weeknd", "country": "Канада", "genre": "Pop"},
    {"id": 2, "name": "Daft Punk", "country": "Франция",
     "genre": "Electronic"},
]


@pytest.fixture
def album():
    return create_album(1, "After Hours", 1, 2020, "Pop", 1, 14)


def test_create_album(album):
    assert album["id"] == 1
    assert album["title"] == "After Hours"
    assert album["artist_id"] == 1
    assert album["user_id"] == 1
    assert album["songs_count"] == 14
    assert album["rating"] is None
    assert album["is_listened"] is False


def test_create_album_empty_title_forbidden():
    with pytest.raises(ValueError):
        create_album(1, "  ", 1, 2020, "Pop", 1)


def test_create_album_future_year_forbidden():
    with pytest.raises(ValueError):
        create_album(1, "Future", 1, date.today().year + 1, "Pop", 1)


def test_create_album_negative_songs_forbidden():
    with pytest.raises(ValueError):
        create_album(1, "Test", 1, 2020, "Pop", 1, -5)


def test_validate_rating():
    assert validate_rating(1)
    assert validate_rating(5)
    assert not validate_rating(0)
    assert not validate_rating(6)


def test_validate_year():
    assert validate_year(2020)
    assert not validate_year(date.today().year + 1)


def test_rate_album(album):
    rate_album(album, 5)
    assert album["rating"] == 5
    assert album["is_listened"]


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_rate_album_invalid(album, rating):
    with pytest.raises(ValueError):
        rate_album(album, rating)
    assert album["rating"] is None


def test_mark_album_listened(album):
    mark_album_listened(album)
    assert album["is_listened"]


def test_album_age(album):
    assert get_album_age(album) == date.today().year - 2020


def test_rating_stars():
    assert get_rating_stars(4) == "★★★★☆"
    assert get_rating_stars(None) == "☆☆☆☆☆"


def test_album_status():
    assert get_album_status(False, None) == "Еще не прослушан"
    assert get_album_status(True, None) == "Прослушан, но не оценён"
    assert get_album_status(True, 5) == "Отличный альбом! Рекомендую!"
    assert get_album_status(True, 3) == "Хороший альбом, стоит послушать"
    assert get_album_status(True, 2) == "Прослушан, но не впечатлил"


def test_recommendation():
    assert "Оцените" in get_recommendation("Pop", None)
    assert "Если вам нравится Pop" in get_recommendation("Pop", 5)
    assert "другие жанры" in get_recommendation("Pop", 1)


@pytest.fixture
def albums():
    first = create_album(1, "After Hours", 1, 2020, "Pop", 1)
    second = create_album(2, "Discovery", 2, 2001, "Electronic", 1)
    third = create_album(3, "Homework", 2, 1997, "Electronic", 1)
    first["rating"] = 5
    second["rating"] = 3
    return [first, second, third]


def test_find_album(albums):
    assert [a["id"] for a in find_album(albums, ARTISTS, "daft")] == [2, 3]
    assert [a["id"] for a in find_album(albums, ARTISTS, "after")] == [1]
    assert find_album(albums, ARTISTS, "zzz") == []


def test_find_album_by_id(albums):
    assert find_album_by_id(albums, 2) is albums[1]
    assert find_album_by_id(albums, 99) is None


def test_filter_albums_by_genre(albums):
    result = filter_albums_by_genre(albums, "electronic")
    assert [a["id"] for a in result] == [2, 3]


def test_sort_albums(albums):
    assert [a["id"] for a in sort_albums(albums, "rating")] == [1, 2, 3]
    assert [a["id"] for a in sort_albums(albums, "year")] == [3, 2, 1]
    assert [a["id"] for a in sort_albums(albums, "title")] == [1, 2, 3]
    with pytest.raises(ValueError):
        sort_albums(albums, "unknown")


def test_format_album(albums):
    assert format_album(albums[0], ARTISTS) == (
        "After Hours — The Weeknd (2020), Pop, ★★★★★, не прослушан"
    )
