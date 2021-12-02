"""Module with orders blueprint routes"""

from flask import Blueprint

from shop.orders.views import orders_list

orders_blueprint = Blueprint('orders_blueprint', __name__)

orders_blueprint.add_url_rule('/orders_list',
                              view_func=orders_list, methods=['GET', 'POST'])
