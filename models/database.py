import sqlite3
from pathlib import Path

# Slovensky komentár: inicializácia databázy a tabuľiek
DB_PATH = Path(__file__).resolve().parent.parent / 'data.db'


def get_connection():
    """Vráti pripojenie na sqlite3."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Vytvorenie potrebných tabuliek ak neexistujú."""
    conn = get_connection()
    cur = conn.cursor()
    # Tabuľka používateľov
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            initial_equity REAL NOT NULL,
            session_token TEXT
        )
        """
    )
    # Tabuľka obchodov
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            risk REAL NOT NULL,
            reward REAL NOT NULL,
            result INTEGER,
            equity_after REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()
