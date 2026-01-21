import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_NAME = "noticias.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Crear tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS news (
            link TEXT PRIMARY KEY,
            title TEXT,
            summary TEXT,
            section TEXT,
            published_date TIMESTAMP,
            sentiment TEXT,
            source TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_news(news_list):
    """
    Guarda una lista de diccionarios con noticias.
    Ignora si el link ya existe.
    """
    if not news_list:
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    for item in news_list:
        try:
            c.execute('''
                INSERT OR IGNORE INTO news (link, title, summary, section, published_date, sentiment, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['link'],
                item['title'],
                item['summary'],
                item['section'],
                item['published_date'],
                item['sentiment'],
                item['source']
            ))
        except Exception as e:
            print(f"Error saving news: {e}")
            
    conn.commit()
    conn.close()

def url_exists(link):
    """
    Returns True if the link already exists in the database.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT 1 FROM news WHERE link = ?', (link,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def get_recent_news(hours=168):
    """
    Obtiene noticias de las últimas 'hours' horas, ordenadas por fecha (relevancia implicita en RSS).
    """
    conn = sqlite3.connect(DB_NAME)
    
    # Calcular fecha límite
    time_threshold = datetime.now() - timedelta(hours=hours)
    
    query = """
        SELECT * FROM news 
        WHERE published_date >= ?
        ORDER BY published_date DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(time_threshold,))
    conn.close()
    return df
