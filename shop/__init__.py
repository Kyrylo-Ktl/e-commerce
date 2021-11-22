"""Module with function for creating app"""

from flask import Flask
from flask_bootstrap import Bootstrap

from shop.db import init_database


def create_app(config_filename: str = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    Bootstrap(app)

    with app.app_context():
        init_database(app)

    return app
