from wsgiref.simple_server import make_server
from urllib.parse import unquote
from models.database import init_db
from routes import auth as auth_routes
from routes import trade as trade_routes
from routes.utils import current_user
import os

# Slovensky komentár: hlavný vstup aplikácie

init_db()


def not_found():
    return ('404 Not Found', [('Content-Type','text/plain')], b'Not Found')


def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = unquote(environ.get('PATH_INFO', ''))

    if path.startswith('/static/'):
        file_path = path.lstrip('/')
        if os.path.exists(file_path):
            start_response('200 OK', [('Content-Type','text/javascript')])
            with open(file_path, 'rb') as f:
                return [f.read()]
        start_response('404 Not Found', [('Content-Type','text/plain')])
        return [b'File not found']

    routes = {
        ('GET', '/'): lambda env: (
            ('302 Found', [('Location', '/dashboard')], b'')
            if current_user(env) else auth_routes.login_get(env)
        ),
        ('POST', '/login'): auth_routes.login_post,
        ('GET', '/register'): auth_routes.register_get,
        ('POST', '/register'): auth_routes.register_post,
        ('GET', '/logout'): auth_routes.logout,
        ('GET', '/dashboard'): trade_routes.dashboard,
        ('POST', '/trade'): trade_routes.trade_post,
    }

    handler = routes.get((method, path))
    if not handler:
        status, headers, body = not_found()
    else:
        status, headers, body = handler(environ)
    start_response(status, headers)
    return [body]


if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
