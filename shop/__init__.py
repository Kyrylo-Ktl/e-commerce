"""Module with function for creating app"""

from flask import Flask
from flask_bootstrap import Bootstrap

from shop.db import init_database
from flask_login import LoginManager
from shop.carts.session_handler import SessionCart


def create_app(config_filename: str = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    Bootstrap(app)

    from shop.email import init_mail
    init_mail(app)

    from shop.products.models import CategoryModel, BrandModel, ProductModel
    from shop.users.models import UserModel
    login_manager = LoginManager(app)
    login_manager.login_view = 'users_blueprint.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    @app.context_processor
    def cart_summary_processor():
        return {
            'cart_size': SessionCart.get_items_count,
            'cart_total': SessionCart.get_total_sum,
        }

    with app.app_context():
        init_database(app)

        from shop.users.routes import users_blueprint
        from shop.products.routes import products_blueprint
        from shop.carts.routes import carts_blueprint
        from shop.orders.routes import orders_blueprint
        app.register_blueprint(users_blueprint)
        app.register_blueprint(products_blueprint)
        app.register_blueprint(carts_blueprint)
        app.register_blueprint(orders_blueprint)

    return app
