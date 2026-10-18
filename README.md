# Maestro — сервис музыкальных коллекций

Приложение для управления личной музыкальной коллекцией: альбомы,
исполнители, оценки, статус прослушивания и рекомендации. Есть
консольная версия (ПР1–ПР3) и веб-интерфейс на Django (ПР5).

## Назначение

Приложение позволяет вести личную музыкальную коллекцию: хранить альбомы
и исполнителей, оценивать прослушанное и получать рекомендации.

## Целевая аудитория

Слушатели музыки, которым нужен простой способ учитывать свои альбомы,
оценки и статус прослушивания.

## Возможности

- вход в систему по имени (новый пользователь регистрируется);
- просмотр коллекции и подробная карточка альбома;
- добавление альбомов и удаление из коллекции;
- оценка альбома (1–5) и отметка «прослушан»;
- поиск по названию альбома или исполнителю;
- фильтрация по жанру и сортировка (оценка, год, название);
- статистика коллекции (песни, альбомы, исполнители, средняя оценка);
- рекомендации на основе оценок;
- сохранение данных между запусками в JSON-файлах.

## Предметная область

Основные сущности: пользователь, исполнитель, альбом, коллекция.
Каждая сущность — класс (`User`, `Artist`, `Album`, `Collection`)
в пакете `models/`; рядом с классом лежат функции поиска и управления
списками объектов. Связи между объектами хранятся ссылками на объекты,
а в JSON записываются идентификаторами.

Бизнес-правила:

- оценка альбома от 1 до 5;
- год выпуска не может быть в будущем;
- название альбома и имя исполнителя не могут быть пустыми;
- один альбом нельзя добавить в коллекцию дважды.

## Основные сущности и классы

### User — пользователь

- атрибуты: `id`, `name`, `registered_at`;
- методы: `from_data()` (classmethod, создание из записи JSON),
  `__str__()`.

### Artist — исполнитель

- атрибуты: `id`, `name`, `country`, `genre`;
- методы: `from_data()` (classmethod), `__str__()`.

### Album — альбом

- атрибуты: `id`, `title`, `artist` (объект `Artist`), `release_year`,
  `genre`, `user` (объект `User`), `songs_count`, `rating`,
  `is_listened`;
- методы: `rate()` (оценка 1–5, альбом считается прослушанным),
  `mark_listened()`, `age()`, `__str__()`;
- статические методы: `validate_rating()`, `validate_year()`.

### Collection — коллекция пользователя

- атрибуты: `id`, `user` (объект `User`), `albums` (список объектов
  `Album`);
- методы: `contains()`, `add_album()`, `remove_album()`, `favorite_genre()`,
  `__str__()`;
- свойства: `total_albums`, `total_songs`, `total_artists`,
  `listened_count`, `average_rating`.

## Взаимодействие объектов

```text
User ──владеет──> Collection ──содержит──> Album ──исполняет──> Artist
  └───────────────────── Album.user ──────────┘
```

- `Album` хранит ссылки на объекты `Artist` и `User`, а не их
  идентификаторы (`album.artist.name`, `album.user.id`);
- `Collection` хранит список объектов `Album` и проверяет, что альбом
  принадлежит владельцу коллекции и не дублируется;
- `add_album_to_collection()` создаёт `Album`, добавляет его в коллекцию
  и в общий список альбомов; `remove_album_from_collection()` удаляет
  из обоих;
- при загрузке `storage.py` по `artist_id`, `user_id` и `album_ids`
  находит объекты и восстанавливает ссылки, при сохранении преобразует
  ссылки обратно в идентификаторы;
- альбом без найденного исполнителя или пользователя не создаётся.

## Формат данных

Данные хранятся в каталоге `data/` в JSON-файлах:

- `users.json` — `id`, `name`, `registered_at`;
- `artists.json` — `id`, `name`, `country`, `genre`;
- `albums.json` — `id`, `title`, `artist_id`, `release_year`, `genre`,
  `songs_count`, `rating`, `is_listened`, `user_id`;
- `collections.json` — `id`, `user_id`, `album_ids`.

Консольная версия читает эти файлы при запуске и сохраняет при
завершении. Некорректный JSON и отсутствующие файлы не приводят к
аварийному завершению программы. Для веб-интерфейса JSON служит
источником данных, перенесённых в базу SQLite (раздел «База данных»).

## Структура проекта

```text
MyProject/
├── README.md
├── requirements.txt
├── pytest.ini
├── .flake8
├── .gitignore
├── manage.py
├── main.py
├── storage.py
├── utils.py
├── db/
│   ├── __init__.py
│   ├── database.py
│   └── import_json.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── maestro/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── base.html
│   ├── 404.html
│   └── includes/
│       └── navigation.html
├── homepage/
│   ├── templatetags/
│   │   └── maestro_tags.py
│   ├── static/homepage/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── img/logo.png
│   ├── templates/homepage/
│   │   └── index.html
│   ├── urls.py
│   └── views.py
├── albums/
│   ├── templates/albums/
│   │   ├── album_list.html
│   │   ├── album_detail.html
│   │   ├── search.html
│   │   ├── statistics.html
│   │   └── includes/
│   │       ├── album_card.html
│   │       └── album_status.html
│   ├── urls.py
│   └── views.py
├── artists/
│   ├── templates/artists/
│   │   ├── artist_list.html
│   │   ├── artist_detail.html
│   │   └── includes/
│   │       └── artist_card.html
│   ├── urls.py
│   └── views.py
├── library/
│   ├── templates/library/
│   │   ├── collection_list.html
│   │   └── collection_detail.html
│   ├── urls.py
│   └── views.py
├── models/
│   ├── __init__.py
│   ├── users.py
│   ├── artists.py
│   ├── albums.py
│   └── collection.py
├── data/
│   ├── users.json
│   ├── artists.json
│   ├── albums.json
│   ├── collections.json
│   └── maestro.sqlite
└── tests/
    ├── test_artists.py
    ├── test_users.py
    ├── test_albums.py
    ├── test_collection.py
    ├── test_storage.py
    ├── test_db.py
    └── test_web.py
```

(в приложениях также есть служебные `admin.py`, `apps.py`, `models.py`,
`tests.py`, `migrations/`, созданные Django.)

## Веб-интерфейс (Django)

Проект использует Django 5.2. Django-проект `maestro` хранит настройки и
маршрутизацию верхнего уровня, а функциональность разделена на четыре
приложения. Приложение коллекций названо `library`, а не `collections`,
чтобы не затенять стандартный модуль Python `collections`.

| URL | Имя маршрута | View-функция | Шаблон |
| --- | --- | --- | --- |
| `/` | `homepage:index` | `homepage.views.index` | `homepage/index.html` |
| `/albums/` | `albums:list` | `albums.views.albums` | `albums/album_list.html` |
| `/albums/<int:album_id>/` | `albums:detail` | `albums.views.album_detail` | `albums/album_detail.html` |
| `/albums/search/` | `albums:search` | `albums.views.search` | `albums/search.html` |
| `/albums/statistics/` | `albums:statistics` | `albums.views.statistics` | `albums/statistics.html` |
| `/artists/` | `artists:list` | `artists.views.artists` | `artists/artist_list.html` |
| `/artists/<int:artist_id>/` | `artists:detail` | `artists.views.artist_detail` | `artists/artist_detail.html` |
| `/collections/` | `library:list` | `library.views.collections` | `library/collection_list.html` |
| `/collections/<int:collection_id>/` | `library:detail` | `library.views.collection_detail` | `library/collection_detail.html` |

Если объект с указанным id не найден, соответствующий шаблон выводит
сообщение «не найдено», а ответ имеет код 404. Для адресов, не подошедших
ни под один маршрут, подключён собственный обработчик
`handler404 = "homepage.views.page_not_found"`, он выводит `404.html`
(работает при `DEBUG=False`).

## Шаблоны Django (ПР6)

HTML больше не формируется в Python: view-функции загружают данные через
`main.load_data()` (тот же `storage.py`, что и в консольной версии),
готовят контекст и вызывают `render(request, шаблон, context)`.
Функция `page()` из ПР5 удалена.

- **Базовый шаблон** `templates/base.html` содержит общую структуру
  страницы, подключение Bootstrap 5.3 (CDN), собственных CSS и JS, логотип,
  подвал и блоки `{% block title %}` и `{% block content %}`. Каталог
  `templates/` подключён в `settings.py` через `TEMPLATES["DIRS"]`.
- **Наследование:** все страницы начинаются с `{% extends "base.html" %}` и
  переопределяют блоки `title` и `content`.
- **Включаемые шаблоны (`{% include %}`):** `includes/navigation.html`
  (навигация), `albums/includes/album_card.html` (карточка альбома),
  `albums/includes/album_status.html` (статус «прослушан / не прослушан»,
  используется в списке, карточке альбома и коллекции),
  `artists/includes/artist_card.html`.
- **Контекст:** например, `{"albums": albums_list}` в списке альбомов;
  в шаблонах `{{ album.title }}`, `{{ album.artist.name }}`.
- **Условия и циклы:** `{% if album %}` ... `{% else %}` для найденного и
  отсутствующего объекта, `{% if album.is_listened %}` для статуса,
  `{% for ... %}` с `{% empty %}` для пустых списков.
- **Именованные URL и пространства имён:** в каждом `urls.py` задан
  `app_name` (`homepage`, `albums`, `artists`, `library`), ссылки строятся
  как `{% url 'albums:detail' album.id %}`, жёстко заданных адресов в
  шаблонах нет.
- **Фильтры:** `|length` («Всего альбомов: N»), `|default:"Без названия"`,
  `|date:"d.m.Y"` (дата регистрации владельца коллекции),
  `|floatformat:1` (средняя оценка).
- **Статические файлы** (`homepage/static/homepage/`): `css/style.css`
  (собственные стили карточек, статуса, логотипа), `js/main.js` (текущий
  год в подвале), `img/logo.png` (логотип). Подключаются через
  `{% load static %}` и `{% static %}`.
- Данные пользователей экранируются автоматически средствами шаблонов.

Django ORM, формы и авторизация пока не используются. Операции изменения
данных (добавление, удаление, оценка) остаются в консольной версии.

## База данных SQLite (ПР7)

Веб-страницы получают данные из реляционной базы `data/maestro.sqlite`
средствами `sqlite3` и SQL-запросов. JSON-файлы остаются источником данных,
который переносится в базу, и данными консольной версии.

```text
SQLite → SQL → sqlite3 → Django view → контекст → шаблон → страница
```

### Таблицы и ключи

| Таблица | Поля (тип) | Ключи |
| --- | --- | --- |
| `users` | `id` INTEGER, `name` TEXT, `registered_at` TEXT (YYYY-MM-DD) | PK `id` |
| `artists` | `id` INTEGER, `name` TEXT, `country` TEXT, `genre` TEXT | PK `id` |
| `albums` | `id` INTEGER, `title` TEXT, `artist_id` INTEGER, `release_year` INTEGER, `genre` TEXT, `songs_count` INTEGER, `rating` INTEGER (NULL — нет оценки, 1–5), `is_listened` INTEGER (0/1), `user_id` INTEGER | PK `id`; FK `artist_id` → `artists.id`, `user_id` → `users.id` |
| `collections` | `id` INTEGER, `user_id` INTEGER | PK `id`; FK `user_id` → `users.id` |
| `collection_albums` | `collection_id` INTEGER, `album_id` INTEGER | составной PK; FK → `collections.id`, `albums.id` |

Связь «коллекция — альбомы» многие ко многим, поэтому список `album_ids`
из JSON хранится в отдельной таблице `collection_albums`. Логическое
значение `is_listened` хранится числом 0 или 1, оценка может быть `NULL`.

### Файлы слоя базы данных

- `sql/schema.sql` — создание таблиц (`CREATE TABLE IF NOT EXISTS`,
  повторный запуск безопасен);
- `sql/queries.sql` — 21 проверенный запрос с комментариями: списки,
  `WHERE`, `JOIN`, `COUNT`/`AVG`/`SUM`, `GROUP BY`, `HAVING`, подзапрос
  `NOT IN`, `DISTINCT`, `LIMIT`/`OFFSET`, проверка `NULL`;
- `db/database.py` — `get_connection()` включает проверку внешних ключей
  (`PRAGMA foreign_keys = ON`), `create_schema()` выполняет `schema.sql`;
- `db/import_json.py` — перенос JSON в таблицы через `executemany()` и
  параметры `?`, с `commit()` и `rollback()` при ошибке; перед импортом
  таблицы очищаются, поэтому скрипт можно запускать повторно.

Пересоздание базы и проверка запросов (из корня проекта):

```text
python -m db.import_json
sqlite3 data/maestro.sqlite < sql/queries.sql
```

### SQL в веб-приложении

Запросы сначала проверяются в SQLite CLI и сохраняются в
`sql/queries.sql`, затем те же тексты используются в представлениях
(`conn.execute(запрос, [параметры])`). Значения передаются только через
параметры `?`, f-строки для подстановки значений не используются. Для
доступа к полям по именам задан `conn.row_factory = sqlite3.Row`.
Тест `test_views_use_the_same_sql_as_queries_file` следит, чтобы SQL в
представлениях совпадал с `queries.sql`.

| Страница | Что получает из SQLite |
| --- | --- |
| `/albums/` | `JOIN` альбомов и исполнителей |
| `/albums/<id>/` | карточка альбома: `JOIN`, `WHERE id = ?` |
| `/albums/search/` | поиск по жанру, оценке и названию (параметры `?`) |
| `/albums/statistics/` | `COUNT`, `AVG`, `SUM`, `GROUP BY`, `HAVING` |
| `/artists/`, `/artists/<id>/` | исполнители с числом альбомов, альбомы исполнителя |
| `/collections/`, `/collections/<id>/` | коллекции, агрегатная статистика, любимый жанр |

Звёзды оценки выводятся шаблонным фильтром `stars`
(`homepage/templatetags/maestro_tags.py`), а не SQL.

## Модули и функции

| Модуль | Назначение и функции |
| --- | --- |
| `main.py` | меню и пользовательские сценарии, `main()` |
| `models/users.py` | класс `User` (`from_data`); `add_user`, `find_user`, `find_user_by_id`, `find_user_by_name`, `show_users` |
| `models/artists.py` | класс `Artist` (`from_data`); `add_artist`, `find_artist`, `find_artist_by_id`, `find_artist_by_name`, `show_artists` |
| `models/albums.py` | класс `Album` (`validate_rating`, `validate_year`, `rate`, `mark_listened`, `age`); `get_rating_stars`, `get_album_status`, `get_recommendation`, `find_album`, `find_album_by_id`, `filter_albums_by_genre`, `sort_albums`, `show_albums` |
| `models/collection.py` | класс `Collection` (`contains`, `add_album`, `remove_album`, `total_albums`, `total_songs`, `total_artists`, `listened_count`, `average_rating`, `favorite_genre`); `create_collection`, `get_user_collection`, `find_collection_by_id`, `add_album_to_collection`, `remove_album_from_collection`, `get_collection_recommendation`, `show_statistics` |
| `maestro/` | настройки и корневые маршруты Django-проекта |
| `homepage/`, `albums/`, `artists/`, `library/` | Django-приложения: `urls.py`, `views.py`, шаблоны (`templates/`), статика (`homepage/static/`) |
| `templates/` | базовый шаблон `base.html`, `404.html`, навигация |
| `db/` | слой базы данных: `database.py` (подключение), `import_json.py` (перенос JSON в SQLite) |
| `sql/` | `schema.sql` (таблицы), `queries.sql` (запросы проекта) |
| `storage.py` | `load_*` / `save_*` для пользователей, исполнителей, альбомов и коллекций |
| `utils.py` | `input_int`, `input_text`, `next_id` |

Функции `get_album_status()`, `get_rating_stars()` и
`get_recommendation()` перенесены из начального сценария ПР1.
Для сортировки используется lambda-функция, для фильтрации — генератор.

## Запуск программы

Установка зависимостей:

```text
pip install -r requirements.txt
```

Веб-версия (Django): сначала создать и заполнить базу SQLite, затем
запустить сервер:

```text
python -m db.import_json
python manage.py migrate
python manage.py runserver --insecure
```

После запуска открыть в браузере `http://127.0.0.1:8000/`.

В `settings.py` стоит `DEBUG = False` (чтобы работала собственная страница
404), а в этом режиме `runserver` не отдаёт статические файлы. Флаг
`--insecure` включает их раздачу для учебного запуска. Без него страницы
открываются, но собственные CSS, JS и логотип не загружаются.

Проверка подключения статических файлов:

```text
python manage.py findstatic homepage/css/style.css
```

Консольная версия:

```text
python main.py
```

## Тестирование

```text
pytest -v
```

Тесты покрывают классы предметной области, хранилище и веб-страницы:
коды ответа 200 и 404, используемые шаблоны и наследование, контекст,
пространства имён URL, фильтры, обработку пустых списков, экранирование
HTML и поиск статических файлов. Тесты `tests/test_db.py` проверяют схему
и ключи, импорт из JSON (количество записей, повторный запуск, NULL),
выполнение всех запросов, их объём и виды, защиту от SQL-инъекций и
совпадение SQL в представлениях с `sql/queries.sql`. Веб-тесты работают
на временной базе.

## Проверка качества кода

```text
flake8 .
```

## План развития

Реализовано: консольное приложение (ПР1–ПР3), веб-интерфейс на Django
(ПР5), перевод веб-части на шаблоны Django со статическими файлами (ПР6),
база данных SQLite, SQL-запросы и страницы на данных из базы (ПР7).

На следующих этапах планируется:

- переход от SQL-запросов к Django ORM и моделям Django;
- формы создания и изменения данных;
- реализация пользователей и авторизации;
- разработка API;
- контейнеризация приложения;
- настройка CI/CD.
