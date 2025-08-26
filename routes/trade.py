import json
from urllib.parse import parse_qs
from models import trade as trade_model
from routes.utils import current_user
from models.database import get_connection

# Slovensky komentár: spracovanie obchodov a dashboardu


def dashboard(environ):
    """Zobrazenie hlavnej stránky s grafom."""
    user = current_user(environ)
    if not user:
        return ('302 Found', [('Location', '/')], b'')
    trades = trade_model.get_trades(user['id'])
    equity = [user['initial_equity']]
    for t in trades:
        equity.append(t['equity_after'])
    html = open('templates/dashboard.html', 'r', encoding='utf-8').read()
    html = html.replace('{{username}}', user['username'])
    html = html.replace('{{equity_data}}', json.dumps(equity))
    return ('200 OK', [('Content-Type', 'text/html; charset=utf-8')], html.encode())


def trade_post(environ):
    """Pridanie výsledku obchodu."""
    user = current_user(environ)
    if not user:
        return ('401 Unauthorized', [('Content-Type','text/plain')], b'Auth required')
    try:
        size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        size = 0
    body = environ['wsgi.input'].read(size).decode()
    data = parse_qs(body)
    risk = float(data.get('risk', ['0'])[0])
    reward = float(data.get('reward', ['0'])[0])
    result = int(data.get('result', ['0'])[0])  # 1 win, -1 loss
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT equity_after FROM trades WHERE user_id=? ORDER BY id DESC LIMIT 1", (user['id'],))
    row = cur.fetchone()
    current_eq = row['equity_after'] if row else user['initial_equity']
    new_eq = current_eq + reward if result == 1 else current_eq - risk
    trade_model.record_trade(user['id'], risk, reward, result, new_eq)
    trades = trade_model.get_trades(user['id'])
    equity = [user['initial_equity']]
    for t in trades:
        equity.append(t['equity_after'])
    resp = json.dumps({'equity': equity}).encode()
    return ('200 OK', [('Content-Type','application/json')], resp)
