from flask import abort
from flask_login import current_user


def admin_required(function):
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_superuser:
            return function(*args, **kwargs)
        return abort(403)

    wrapper.__name__ = function.__name__
    return wrapper
