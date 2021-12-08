from random import randint
import unittest

from flask import session
from flask_login import current_user, login_user, logout_user
from tests.mixins import ClientRequestsMixin, UserMixin

from shop.carts.session_handler import SessionCart
from shop.orders.models import OrderModel
from shop.products.models import ProductModel
from shop.seed_db import (
    get_random_product_data,
    seed_products
)


class SessionCartTests(UserMixin, ClientRequestsMixin):
    def setUp(self):
        login_user(self.user)
        SessionCart.init_cart()

    def tearDown(self):
        SessionCart.clear_cart()
        logout_user()
        for pr in ProductModel.get_all():
            pr.delete()
        for order in OrderModel.get_all():
            order.delete()

    def test_cart_exists_in_session(self):
        self.assertTrue(SessionCart.CART_NAME in session)
        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_add_one_product(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        self.assertEqual(product.reserved, amount_to_add)
        self.assertTrue(str(product.id) in session[SessionCart.CART_NAME])

    def test_add_one_product_twice(self):
        product = ProductModel.create(**get_random_product_data())

        SessionCart.add_product(product.id, 1)
        SessionCart.add_product(product.id, 1)

        self.assertEqual(product.reserved, 2)
        self.assertTrue(str(product.id) in session[SessionCart.CART_NAME])

    def test_add_several_products(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)

        for pr in ProductModel.get_all():
            self.assertTrue(str(pr.id) in session[SessionCart.CART_NAME])

    def test_add_negative_product_amount(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = -randint(1, product.amount)

        with self.assertRaises(ValueError):
            SessionCart.add_product(product.id, amount_to_add)

        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_add_more_than_exists_product_amount(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = product.amount + randint(1, 10)

        with self.assertRaises(ValueError):
            SessionCart.add_product(product.id, amount_to_add)

        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_remove_full_product_amount(self):
        product = ProductModel.create(**get_random_product_data())
        product_amount = randint(1, product.amount)

        SessionCart.add_product(product.id, product_amount)
        SessionCart.remove_product(product.id, product_amount)
        self.assertEqual(product.reserved, 0)
        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_remove_part_of_product_amount(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(2, product.amount)
        amount_to_remove = randint(1, amount_to_add // 2)

        SessionCart.add_product(product.id, amount_to_add)
        SessionCart.remove_product(product.id, amount_to_remove)

        self.assertEqual(product.reserved, amount_to_add - amount_to_remove)
        self.assertTrue(str(product.id) in session[SessionCart.CART_NAME])

    def test_remove_negative_amount(self):
        product = ProductModel.create(**get_random_product_data())
        SessionCart.add_product(product.id, 1)
        amount_to_remove = -randint(0, 10)

        with self.assertRaises(ValueError) as context:
            SessionCart.remove_product(product.id, amount_to_remove)

        self.assertTrue('The amount to remove cannot be negative' in str(context.exception))
        self.assertEqual(product.reserved, 1)
        self.assertTrue(str(product.id) in session[SessionCart.CART_NAME])

    def test_remove_product_which_not_in_cart(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_remove = randint(1, product.amount)

        with self.assertRaises(ValueError) as context:
            SessionCart.remove_product(product.id, amount_to_remove)

        self.assertTrue('Product not in cart' in str(context.exception))
        self.assertEqual(product.reserved, 0)
        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_remove_too_much_product(self):
        product = ProductModel.create(**get_random_product_data())
        SessionCart.add_product(product.id, 1)

        with self.assertRaises(ValueError) as context:
            SessionCart.remove_product(product.id, 2)

        self.assertTrue('Not enough product in cart to remove' in str(context.exception))
        self.assertEqual(product.reserved, 1)
        self.assertTrue(str(product.id) in session[SessionCart.CART_NAME])

    def test_empty_cart_get_items_count(self):
        self.assertEqual(SessionCart.get_items_count(), 0)

    def test_empty_cart_get_total_sum(self):
        self.assertEqual(SessionCart.get_total_sum(), 0)

    def test_empty_cart_get_products(self):
        self.assertEqual(SessionCart.get_products().all(), [])

    def test_empty_cart_get_items(self):
        self.assertEqual(SessionCart.get_items(), [])

    def test_cart_with_one_item_get_items_count(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        self.assertEqual(SessionCart.get_items_count(), amount_to_add)

    def test_cart_with_one_item_get_total_sum(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        expected_sum = amount_to_add * product.discount_price
        self.assertTrue(abs(SessionCart.get_total_sum() - expected_sum) <= 1e-3)

    def test_cart_with_one_item_get_products(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        self.assertEqual(SessionCart.get_products().all(), [product])

    def test_cart_with_one_item_get_items(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        self.assertEqual(SessionCart.get_items(), [(product, amount_to_add)])

    def test_cart_with_many_items_get_items_count(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)

        self.assertEqual(SessionCart.get_items_count(), n_products)

    def test_cart_with_many_items_get_total_sum(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)

        expected_sum = sum(pr.discount_price for pr in ProductModel.get_all())
        self.assertTrue(abs(SessionCart.get_total_sum() - expected_sum) <= 1e-3)

    def test_cart_with_many_items_get_products(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)

        expected_products = set(ProductModel.get_all())
        self.assertSetEqual(expected_products, set(SessionCart.get_products().all()))

    def test_cart_with_many_items_get_items(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)

        expected_items = set(zip(ProductModel.get_all(), [1] * n_products))
        self.assertSetEqual(expected_items, set(SessionCart.get_items()))

    def test_clear_empty_cart(self):
        SessionCart.clear_cart()
        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_clear_cart_with_one_product(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        SessionCart.clear_cart()

        self.assertEqual(product.reserved, 0)
        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_clear_cart_with_several_products(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)
        SessionCart.clear_cart()

        for pr in ProductModel.get_all():
            self.assertEqual(pr.reserved, 0)
        self.assertEqual(session[SessionCart.CART_NAME], {})

    def test_make_order_from_empty_cart(self):
        with self.assertRaises(Exception) as context:
            SessionCart.make_order()

        self.assertTrue('Unable to place an order from an empty cart' in str(context.exception))

    def test_make_order_with_one_product(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        SessionCart.add_product(product.id, amount_to_add)
        SessionCart.make_order()

        self.assertEqual(session[SessionCart.CART_NAME], {})
        self.assertEqual(product.reserved, amount_to_add)

        order = OrderModel.get_random()
        self.assertEqual(order.user, current_user)
        self.assertEqual(order.products.first().amount, amount_to_add)
        self.assertEqual(order.products.first().product, product)

    def test_make_order_with_several_products(self):
        n_products = randint(2, 10)
        seed_products(n_products)

        for pr in ProductModel.get_all():
            SessionCart.add_product(pr.id, 1)
        SessionCart.make_order()

        self.assertEqual(session[SessionCart.CART_NAME], {})
        for pr in ProductModel.get_all():
            self.assertEqual(pr.reserved, 1)

        order = OrderModel.get_random()
        self.assertEqual(order.user, current_user)

        expected_products = set(ProductModel.get_all())
        actual_products = set(item.product for item in order.products.all())
        self.assertSetEqual(expected_products, actual_products)

        expected_amounts = set((pr.id, 1) for pr in ProductModel.get_all())
        actual_amounts = set((item.product.id, item.amount) for item in order.products.all())
        self.assertEqual(expected_amounts, actual_amounts)


if __name__ == "__main__":
    unittest.main()
