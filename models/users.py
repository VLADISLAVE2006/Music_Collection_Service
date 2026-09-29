"""Класс пользователя и функции работы с пользователями."""
from datetime import date
from typing import List, Optional

from utils import next_id


class User:
    """Пользователь сервиса музыкальных коллекций."""

    def __init__(
        self,
        user_id: int,
        name: str,
        registered_at: date,
    ) -> None:
        """Создать пользователя.

        Raises:
            ValueError: если имя пользователя пустое.
        """
        if not name.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        self.id = user_id
        self.name = name.strip()
        self.registered_at = registered_at

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря (запись JSON)."""
        return cls(
            user_id=data["id"],
            name=data["name"],
            registered_at=date.fromisoformat(data["registered_at"]),
        )

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        registered = self.registered_at.strftime("%d.%m.%Y")
        return f"{self.name} (зарегистрирован {registered})"


def add_user(
    users: List[User],
    name: str,
    registered_at: Optional[date] = None,
) -> User:
    """Создать пользователя, добавить в коллекцию и вернуть его."""
    user = User(next_id(users), name, registered_at or date.today())
    users.append(user)
    return user


def find_user(users: List[User], query: str) -> List[User]:
    """Найти пользователей по подстроке имени (без учёта регистра)."""
    query = query.strip().lower()
    return [user for user in users if query in user.name.lower()]


def find_user_by_id(users: List[User], user_id: int) -> Optional[User]:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def find_user_by_name(users: List[User], name: str) -> Optional[User]:
    """Найти пользователя по точному имени (без учёта регистра)."""
    name = name.strip().lower()
    for user in users:
        if user.name.lower() == name:
            return user
    return None


def show_users(users: List[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Список пользователей пуст.")
        return
    for user in users:
        print(f"[{user.id}] {user}")
