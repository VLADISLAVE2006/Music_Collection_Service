from datetime import date

import pytest

from models import User
from models.users import add_user, find_user, find_user_by_name


def test_user_creation():
    user = User(1, "Алексей", date(2026, 9, 1))
    assert user.id == 1
    assert user.name == "Алексей"
    assert user.registered_at == date(2026, 9, 1)


def test_user_str():
    user = User(1, "Алексей", date(2026, 9, 1))
    assert str(user) == "Алексей (зарегистрирован 01.09.2026)"


def test_user_empty_name_forbidden():
    with pytest.raises(ValueError):
        User(1, "", date(2026, 9, 1))


def test_user_from_data():
    user = User.from_data(
        {"id": 3, "name": "Мария", "registered_at": "2026-01-15"}
    )
    assert user.id == 3
    assert user.registered_at == date(2026, 1, 15)


def test_add_and_find_user():
    users = []
    user = add_user(users, "Мария")
    assert users == [user]
    assert user.registered_at == date.today()
    assert find_user(users, "мар") == [user]
    assert find_user_by_name(users, "МАРИЯ") is user
    assert find_user_by_name(users, "Иван") is None
