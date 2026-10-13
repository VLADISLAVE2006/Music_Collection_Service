from datetime import date

import pytest

from models import Album, Artist, Collection, User
from models.collection import (
    add_album_to_collection,
    create_collection,
    find_collection_by_id,
    get_collection_recommendation,
    get_user_collection,
    remove_album_from_collection,
)


@pytest.fixture
def user():
    return User(1, "Алексей", date(2026, 9, 1))


@pytest.fixture
def artist():
    return Artist(1, "The Weeknd", "Канада", "Pop")


@pytest.fixture
def collection(user):
    return Collection(1, user)


def test_collection_starts_empty(collection):
    assert collection.albums == []
    assert collection.total_albums == 0
    assert collection.average_rating is None
    assert collection.favorite_genre() is None


def test_add_album_to_collection(collection, artist, user):
    albums = []
    album = add_album_to_collection(
        collection, albums, "After Hours", artist, 2020, "Pop", 14
    )
    assert album is not None
    assert album.user is user
    assert collection.albums == [album]
    assert albums == [album]


def test_duplicate_album_forbidden(collection, artist):
    albums = []
    add_album_to_collection(collection, albums, "After Hours", artist,
                            2020, "Pop", 14)
    second = add_album_to_collection(collection, albums, "after hours",
                                     artist, 2020, "Pop", 14)
    assert second is None
    assert collection.total_albums == 1
    assert len(albums) == 1


def test_add_album_of_other_user_forbidden(collection, artist):
    other = User(2, "Мария", date(2026, 9, 2))
    album = Album(1, "After Hours", artist, 2020, "Pop", other)
    with pytest.raises(ValueError):
        collection.add_album(album)


def test_remove_album(collection, artist):
    albums = []
    album = add_album_to_collection(collection, albums, "After Hours",
                                    artist, 2020, "Pop", 14)
    assert remove_album_from_collection(collection, albums, album.id)
    assert collection.albums == []
    assert albums == []
    assert not remove_album_from_collection(collection, albums, album.id)


def test_removed_album_can_be_added_again(collection, artist):
    albums = []
    first = add_album_to_collection(collection, albums, "After Hours",
                                    artist, 2020, "Pop", 14)
    remove_album_from_collection(collection, albums, first.id)
    again = add_album_to_collection(collection, albums, "After Hours",
                                    artist, 2020, "Pop", 14)
    assert again is not None


def test_invalid_album_data_raises(collection, artist):
    with pytest.raises(ValueError):
        add_album_to_collection(collection, [], "", artist, 2020, "Pop")


def test_statistics(collection, artist):
    other_artist = Artist(2, "Daft Punk", "Франция", "Electronic")
    albums = []
    first = add_album_to_collection(collection, albums, "After Hours",
                                    artist, 2020, "Pop", 14)
    second = add_album_to_collection(collection, albums, "Discovery",
                                     other_artist, 2001, "Electronic", 14)
    first.rate(5)
    second.rate(3)
    assert collection.total_albums == 2
    assert collection.total_songs == 28
    assert collection.total_artists == 2
    assert collection.listened_count == 2
    assert collection.average_rating == 4
    assert collection.favorite_genre() == "Pop"
    assert "Pop" in get_collection_recommendation(collection)


def test_recommendation_without_ratings(collection):
    assert "Оцените" in get_collection_recommendation(collection)


def test_create_and_get_user_collection(user):
    collections = []
    created = create_collection(collections, user)
    assert get_user_collection(collections, user) is created
    other = User(2, "Мария", date(2026, 9, 2))
    assert get_user_collection(collections, other) is None


def test_find_collection_by_id(user):
    collections = []
    created = create_collection(collections, user)
    assert find_collection_by_id(collections, created.id) is created
    assert find_collection_by_id(collections, 99) is None
