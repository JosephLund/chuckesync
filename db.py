# db.py
import sqlite3
from app import app

DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            token BLOB,
            is_admin INTEGER DEFAULT 0,
            last_synced_id TEXT
        )
    """)
    return conn