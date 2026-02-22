import sqlite3
import os

DB_PATH = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for chip designs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS designs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        path TEXT,
        last_run_id TEXT,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table for generated posts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        design_name TEXT,
        content TEXT,
        status TEXT DEFAULT 'pending',
        readiness_score TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def save_design(name, path, last_run=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO designs (name, path, last_run_id, last_updated)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (name, path, last_run))
    conn.commit()
    conn.close()

def save_pending_post(design_name, content, score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Mark old pending posts for this design as cancelled
    cursor.execute("UPDATE posts SET status = 'cancelled' WHERE design_name = ? AND status = 'pending'", (design_name,))
    
    cursor.execute('''
    INSERT INTO posts (design_name, content, readiness_score)
    VALUES (?, ?, ?)
    ''', (design_name, content, score))
    conn.commit()
    conn.close()

def get_latest_pending_post():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content, design_name FROM posts WHERE status = 'pending' ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

def mark_post_published(content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET status = 'published' WHERE content = ?", (content,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
