"""Module with a class for working with a cart stored in a session"""

from flask import session
from flask_login import current_user

from shop.orders.models import OrderModel
from shop.products.models import ProductModel


class SessionCart:
    """Class for working with cart stored in a session"""

    CART_NAME = 'cart'

    @classmethod
    def init_cart(cls):
        session[cls.CART_NAME] = dict()

    @classmethod
    def add_product(cls, product_id: int, amount: int = 1):
        product = ProductModel.get(id=product_id)
        product_id = str(product_id)

        if amount <= 0:
            raise Exception('The amount to add cannot be negative')
        if amount > product.available:
            raise Exception('Not enough product to add')

        if product_id in session[cls.CART_NAME]:
            session[cls.CART_NAME][product_id] += amount
        else:
            session[cls.CART_NAME][product_id] = amount

        product.reserved += amount
        product.save()
        session.modified = True

    @classmethod
    def remove_product(cls, product_id: int, amount: int = 1):
        product = ProductModel.get(id=product_id)
        product_id = str(product_id)

        if amount <= 0:
            raise Exception('The amount to remove cannot be negative')
        if product_id not in session[cls.CART_NAME]:
            raise Exception('Product not in cart')

        if session[cls.CART_NAME][product_id] < amount:
            raise Exception('Not enough product in cart to remove')
        elif session[cls.CART_NAME][product_id] == amount:
            session[cls.CART_NAME].pop(product_id)
        else:
            session[cls.CART_NAME][product_id] -= amount

        product.reserved -= amount
        product.save()
        session.modified = True

    @classmethod
    def update_product_amount(cls, product_id: int, amount: int):
        amount_change = amount - session[cls.CART_NAME].get(str(product_id), 0)

        if amount_change < 0:
            amount_change = -amount_change
            cls.remove_product(product_id, amount_change)
        elif amount_change > 0:
            cls.add_product(product_id, amount_change)

    @classmethod
    def get_items_count(cls):
        if cls.CART_NAME not in session:
            return 0

        amounts_sum = sum(session[cls.CART_NAME].values())
        return amounts_sum

    @classmethod
    def get_total_sum(cls):
        if cls.CART_NAME not in session:
            return 0

        items = cls.get_items()
        total_sum = sum(pr.discount_price * amount for pr, amount in items)
        return round(total_sum, 2)

    @classmethod
    def get_products(cls):
        ids = session[cls.CART_NAME].keys()
        products = ProductModel.query.filter(ProductModel.id.in_(ids))
        return products

    @classmethod
    def get_items(cls):
        products = cls.get_products()
        items = [(pr, session[cls.CART_NAME][str(pr.id)]) for pr in products.all()]
        return items

    @classmethod
    def clear_cart(cls):
        for product, amount in cls.get_items():
            product.reserved -= amount
            product.save()
            session[cls.CART_NAME].pop(str(product.id))

        session.modified = True

    @classmethod
    def make_order(cls):
        order = OrderModel.create(user=current_user)
        for product, amount in cls.get_items():
            order.add_product(product, amount=amount)
            session[cls.CART_NAME].pop(str(product.id))

        session.modified = True
