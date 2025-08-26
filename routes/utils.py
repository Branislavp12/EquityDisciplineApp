from http.cookies import SimpleCookie
from models import user as user_model

# Slovensky komentár: pomocné funkcie pre routy


def current_user(environ):
    """Získanie aktuálne prihláseného používateľa."""
    cookies = SimpleCookie(environ.get('HTTP_COOKIE', ''))
    token = cookies.get('session')
    if token:
        return user_model.get_user_by_token(token.value)
    return None
