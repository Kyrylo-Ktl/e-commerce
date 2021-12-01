"""Module with utils"""

from flask import abort, current_app
from flask_login import current_user
from itsdangerous import exc, URLSafeTimedSerializer


def admin_required(function):
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_superuser:
            return function(*args, **kwargs)
        return abort(403)

    wrapper.__name__ = function.__name__
    return wrapper


def generate_confirmation_token(email: str):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except exc.BadSignature:
        return None
    else:
        return email
