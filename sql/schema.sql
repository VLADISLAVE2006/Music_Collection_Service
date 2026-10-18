-- ==========================================
-- Maestro: структура базы данных SQLite
-- ==========================================

-- Пользователи сервиса
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    registered_at TEXT NOT NULL
);

-- Исполнители
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    genre TEXT NOT NULL
);

-- Альбомы: оценка может отсутствовать (NULL), is_listened: 0 или 1
CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    artist_id INTEGER NOT NULL,
    release_year INTEGER NOT NULL,
    genre TEXT NOT NULL,
    songs_count INTEGER NOT NULL DEFAULT 0,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    is_listened INTEGER NOT NULL DEFAULT 0 CHECK (is_listened IN (0, 1)),
    user_id INTEGER NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Коллекции пользователей
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Состав коллекций: связь «многие ко многим» между коллекциями и альбомами
CREATE TABLE IF NOT EXISTS collection_albums (
    collection_id INTEGER NOT NULL,
    album_id INTEGER NOT NULL,
    PRIMARY KEY (collection_id, album_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id),
    FOREIGN KEY (album_id) REFERENCES albums(id)
);
