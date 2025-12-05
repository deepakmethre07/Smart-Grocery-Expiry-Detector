# db.py
import sqlite3
from datetime import datetime

DB = 'grocery.db'


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            raw_text TEXT,
            expiry_date TEXT,
            added_on TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_item(name, raw_text, expiry_date):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        'INSERT INTO items (name, raw_text, expiry_date, added_on) VALUES (?, ?, ?, ?)',
        (name, raw_text, expiry_date, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def list_items():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, name, expiry_date, added_on FROM items ORDER BY expiry_date')
    rows = c.fetchall()
    conn.close()
    return rows
