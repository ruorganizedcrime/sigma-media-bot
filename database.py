# database.py
import sqlite3
import datetime
from typing import List, Dict, Optional, Tuple
import difflib

DB_NAME = 'media_bot.db'

def get_db_connection():
    """Создает соединение с базой данных"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица медиа (фильмы, сериалы, аниме)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            year INTEGER,
            genre TEXT,
            type TEXT NOT NULL,
            total_episodes INTEGER DEFAULT 0,
            total_seasons INTEGER DEFAULT 1,
            thumbnail TEXT,
            uploaded_by INTEGER,
            upload_date TEXT,
            imdb REAL
        )
    ''')
    
    # Таблица серий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_id INTEGER NOT NULL,
            season_number INTEGER NOT NULL,
            episode_number INTEGER NOT NULL,
            title TEXT,
            file_id TEXT NOT NULL,
            file_type TEXT DEFAULT 'video',
            duration INTEGER,
            thumbnail TEXT,
            FOREIGN KEY (media_id) REFERENCES media (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== MEDIA FUNCTIONS ====================

def add_media(title: str, description: str, year: int, genre: str, type: str, 
              total_seasons: int, uploaded_by: int, imdb: float = None, thumbnail: str = None) -> int:
    """Добавляет новый медиа-контент"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    upload_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO media (title, description, year, genre, type, total_seasons, 
                          thumbnail, uploaded_by, upload_date, imdb)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, year, genre, type, total_seasons, thumbnail, 
          uploaded_by, upload_date, imdb))
    
    media_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return media_id

def get_media_by_id(media_id: int) -> Optional[Dict]:
    """Получает медиа по ID"""
    conn = get_db_connection()
    media = conn.execute('SELECT * FROM media WHERE id = ?', (media_id,)).fetchone()
    conn.close()
    return dict(media) if media else None

def get_all_media() -> List[Dict]:
    """Получает все медиа"""
    conn = get_db_connection()
    media = conn.execute('SELECT * FROM media ORDER BY upload_date DESC').fetchall()
    conn.close()
    return [dict(item) for item in media]

def get_latest_media(limit: int = 10) -> List[Dict]:
    """Получает последние добавленные медиа"""
    conn = get_db_connection()
    media = conn.execute('''
        SELECT * FROM media 
        ORDER BY upload_date DESC 
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(item) for item in media]

def fuzzy_search_media(query: str, limit: int = 20) -> List[Dict]:
    """Нечеткий поиск по названию, жанру и описанию"""
    if not query:
        return get_latest_media(limit)
    
    conn = get_db_connection()
    all_media = conn.execute('SELECT * FROM media').fetchall()
    conn.close()
    
    results = []
    query_lower = query.lower()
    
    for item in all_media:
        media_dict = dict(item)
        
        # Точные совпадения (высокий приоритет)
        title_lower = media_dict['title'].lower()
        genre_lower = media_dict['genre'].lower() if media_dict['genre'] else ""
        desc_lower = media_dict['description'].lower() if media_dict['description'] else ""
        
        # Проверка на точное совпадение
        exact_title = query_lower in title_lower
        exact_genre = query_lower in genre_lower
        exact_desc = query_lower in desc_lower
        
        if exact_title or exact_genre or exact_desc:
            media_dict['relevance'] = 100 + (10 if exact_title else 0)
            results.append(media_dict)
            continue
        
        # Нечеткое совпадение для названия
        title_ratio = difflib.SequenceMatcher(None, query_lower, title_lower).ratio()
        if title_ratio > 0.6:  # Порог схожести
            media_dict['relevance'] = int(title_ratio * 100)
            results.append(media_dict)
            continue
        
        # Нечеткое совпадение для жанра и описания
        if genre_lower:
            genre_words = genre_lower.replace(',', ' ').split()
            for word in genre_words:
                if difflib.SequenceMatcher(None, query_lower, word).ratio() > 0.7:
                    media_dict['relevance'] = 70
                    results.append(media_dict)
                    break
        
        if media_dict not in results and desc_lower:
            desc_words = desc_lower.split()[:10]  # Только первые 10 слов для оптимизации
            for word in desc_words:
                if len(word) > 3 and difflib.SequenceMatcher(None, query_lower, word).ratio() > 0.7:
                    media_dict['relevance'] = 60
                    results.append(media_dict)
                    break
    
    # Сортировка по релевантности
    results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    return results[:limit]

def delete_media(media_id: int) -> bool:
    """Удаляет медиа и все его серии"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM media WHERE id = ?', (media_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_media_episodes_count(media_id: int, total_episodes: int):
    """Обновляет общее количество серий"""
    conn = get_db_connection()
    conn.execute('UPDATE media SET total_episodes = ? WHERE id = ?', 
                (total_episodes, media_id))
    conn.commit()
    conn.close()

# ==================== EPISODES FUNCTIONS ====================

def add_episode(media_id: int, season_number: int, episode_number: int, 
                file_id: str, title: str = None, thumbnail: str = None, duration: int = None):
    """Добавляет серию"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO episodes (media_id, season_number, episode_number, title, 
                             file_id, thumbnail, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (media_id, season_number, episode_number, title, file_id, thumbnail, duration))
    conn.commit()
    conn.close()

def get_episodes_by_media(media_id: int) -> List[Dict]:
    """Получает все серии медиа"""
    conn = get_db_connection()
    episodes = conn.execute('''
        SELECT * FROM episodes 
        WHERE media_id = ? 
        ORDER BY season_number, episode_number
    ''', (media_id,)).fetchall()
    conn.close()
    return [dict(ep) for ep in episodes]

def get_episodes_by_season(media_id: int, season: int) -> List[Dict]:
    """Получает серии конкретного сезона"""
    conn = get_db_connection()
    episodes = conn.execute('''
        SELECT * FROM episodes 
        WHERE media_id = ? AND season_number = ?
        ORDER BY episode_number
    ''', (media_id, season)).fetchall()
    conn.close()
    return [dict(ep) for ep in episodes]

def get_episode(media_id: int, season: int, episode: int) -> Optional[Dict]:
    """Получает конкретную серию"""
    conn = get_db_connection()
    episode = conn.execute('''
        SELECT * FROM episodes 
        WHERE media_id = ? AND season_number = ? AND episode_number = ?
    ''', (media_id, season, episode)).fetchone()
    conn.close()
    return dict(episode) if episode else None

# ==================== STATISTICS ====================

def get_statistics() -> Dict:
    """Получает статистику"""
    conn = get_db_connection()
    
    stats = {}
    
    # Общее количество
    stats['total'] = conn.execute('SELECT COUNT(*) FROM media').fetchone()[0]
    
    # По типам
    stats['movies'] = conn.execute('SELECT COUNT(*) FROM media WHERE type = "movie"').fetchone()[0]
    stats['series'] = conn.execute('SELECT COUNT(*) FROM media WHERE type = "series"').fetchone()[0]
    stats['anime_movies'] = conn.execute('SELECT COUNT(*) FROM media WHERE type = "anime_movie"').fetchone()[0]
    stats['anime_series'] = conn.execute('SELECT COUNT(*) FROM media WHERE type = "anime_series"').fetchone()[0]
    
    # Всего серий
    stats['total_episodes'] = conn.execute('SELECT COUNT(*) FROM episodes').fetchone()[0]
    
    conn.close()
    return stats

# Инициализация БД при импорте
init_db()