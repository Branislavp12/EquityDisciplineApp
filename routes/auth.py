from urllib.parse import parse_qs
from http.cookies import SimpleCookie
from models import user as user_model
from models.database import get_connection

# Slovensky komentár: spracovanie autentifikácie


def login_get(environ):
    """Zobrazenie prihlasovacieho formulára."""
    return (
        '200 OK',
        [('Content-Type', 'text/html; charset=utf-8')],
        open('templates/login.html', 'r', encoding='utf-8').read().encode()
    )


def login_post(environ):
    """Spracovanie prihlasovania."""
    try:
        size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        size = 0
    body = environ['wsgi.input'].read(size).decode()
    data = parse_qs(body)
    username = data.get('username', [''])[0]
    password = data.get('password', [''])[0]
    token = user_model.authenticate(username, password)
    if token:
        headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Location', '/dashboard'),
            ('Set-Cookie', f'session={token}; HttpOnly; Path=/')
        ]
        return ('302 Found', headers, b'')
    else:
        return (
            '401 Unauthorized',
            [('Content-Type', 'text/html; charset=utf-8')],
            b'Invalid credentials'
        )


def register_get(environ):
    """Zobrazenie registračného formulára."""
    return (
        '200 OK',
        [('Content-Type', 'text/html; charset=utf-8')],
        open('templates/register.html', 'r', encoding='utf-8').read().encode()
    )


def register_post(environ):
    """Spracovanie registrácie."""
    try:
        size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        size = 0
    body = environ['wsgi.input'].read(size).decode()
    data = parse_qs(body)
    username = data.get('username', [''])[0]
    password = data.get('password', [''])[0]
    equity = float(data.get('equity', ['0'])[0])
    if user_model.create_user(username, password, equity):
        headers = [('Location', '/')]  # redirect to login
        return ('302 Found', headers, b'')
    return (
        '400 Bad Request',
        [('Content-Type', 'text/html; charset=utf-8')],
        b'User creation failed'
    )


def logout(environ):
    """Odhlásenie používateľa."""
    cookies = SimpleCookie(environ.get('HTTP_COOKIE', ''))
    token = cookies.get('session')
    if token:
        conn = get_connection()
        conn.execute("UPDATE users SET session_token=NULL WHERE session_token=?", (token.value,))
        conn.commit()
        conn.close()
    headers = [('Location', '/') , ('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/')]
    return ('302 Found', headers, b'')
