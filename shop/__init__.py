"""Module with function for creating app"""

from flask import Flask
from flask_bootstrap import Bootstrap

from shop.db import init_database
from flask_login import LoginManager


def create_app(config_filename: str = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    Bootstrap(app)

    from shop.users.models import UserModel
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    with app.app_context():
        init_database(app)

        from shop.core.routes import core_blueprint
        from shop.users.routes import users_blueprint
        app.register_blueprint(core_blueprint)
        app.register_blueprint(users_blueprint)

    return app
