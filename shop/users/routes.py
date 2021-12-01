"""Module with users blueprint routes"""

from flask import Blueprint

from shop.users.views import (
    confirm_email,
    login,
    logout,
    signup,
)

users_blueprint = Blueprint('users_blueprint', __name__)

users_blueprint.add_url_rule('/confirm/<token>',
                             view_func=confirm_email, methods=['GET'])
users_blueprint.add_url_rule('/login',
                             view_func=login, methods=['GET', 'POST'])
users_blueprint.add_url_rule('/logout',
                             view_func=logout, methods=['GET'])
users_blueprint.add_url_rule('/signup',
                             view_func=signup, methods=['GET', 'POST'])
