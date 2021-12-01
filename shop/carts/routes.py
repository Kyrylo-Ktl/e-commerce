"""Module with carts blueprint routes"""

from flask import Blueprint

from shop.carts.views import cart

carts_blueprint = Blueprint('carts_blueprint', __name__)

carts_blueprint.add_url_rule('/cart',
                             view_func=cart, methods=['GET', 'POST'])
