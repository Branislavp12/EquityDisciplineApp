import hashlib
import secrets
from .database import get_connection

# Slovensky komentár: operácie s používateľmi


def hash_password(password: str) -> str:
    """Vytvorenie hash-u hesla."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str, initial_equity: float) -> bool:
    """Vloženie nového používateľa."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, initial_equity) VALUES (?, ?, ?)",
            (username, hash_password(password), initial_equity),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def authenticate(username: str, password: str) -> str | None:
    """Overenie prihlasovacích údajov. Vráti session token."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if row and row["password_hash"] == hash_password(password):
        token = secrets.token_hex(16)
        conn.execute("UPDATE users SET session_token = ? WHERE id = ?", (token, row["id"]))
        conn.commit()
        conn.close()
        return token
    conn.close()
    return None


def get_user_by_token(token: str):
    """Získanie používateľa podľa session tokenu."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE session_token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return row

