"""Module with users blueprint routes"""

from flask import Blueprint

from shop.users import views

users_blueprint = Blueprint('users_blueprint', __name__)

users_blueprint.add_url_rule('/confirm/<token>',
                             view_func=views.confirm_email, methods=['GET'])
users_blueprint.add_url_rule('/login',
                             view_func=views.login, methods=['GET', 'POST'])
users_blueprint.add_url_rule('/logout',
                             view_func=views.logout, methods=['GET'])
users_blueprint.add_url_rule('/profile',
                             view_func=views.profile, methods=['GET', 'POST'])
users_blueprint.add_url_rule('/reset_password_request',
                             view_func=views.reset_password_request, methods=['GET', 'POST'])
users_blueprint.add_url_rule('/reset_password/<token>',
                             view_func=views.reset_password, methods=['GET', 'POST'])
users_blueprint.add_url_rule('/signup',
                             view_func=views.signup, methods=['GET', 'POST'])
users_blueprint.add_url_rule('/update_password',
                             view_func=views.update_password, methods=['GET', 'POST'])
