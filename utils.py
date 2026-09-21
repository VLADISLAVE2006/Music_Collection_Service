"""Вспомогательные функции: безопасный ввод и генерация идентификаторов."""
from typing import Any, Optional, Sequence


def input_int(
    prompt: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> int:
    """Запросить у пользователя целое число.

    При некорректном вводе или выходе за границы запрос повторяется.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ошибка: нужно ввести целое число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Ошибка: значение не может быть меньше {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Ошибка: значение не может быть больше {max_value}.")
            continue
        return value


def input_text(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Ошибка: значение не может быть пустым.")


def next_id(items: Sequence[Any]) -> int:
    """Вернуть следующий свободный идентификатор для коллекции объектов."""
    return max((item.id for item in items), default=0) + 1
