from .database import get_connection

# Slovensky komentár: operácie súvisiace s obchodmi


def record_trade(user_id: int, risk: float, reward: float, result: int, equity_after: float):
    """Uloženie výsledku obchodu."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO trades (user_id, risk, reward, result, equity_after) VALUES (?, ?, ?, ?, ?)",
        (user_id, risk, reward, result, equity_after),
    )
    conn.commit()
    conn.close()


def get_trades(user_id: int):
    """Získanie všetkých obchodov používateľa."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trades WHERE user_id = ? ORDER BY id", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
