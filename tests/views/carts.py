from random import randint
import unittest

from flask import url_for
from tests.mixins import ClientRequestsMixin, SuperuserMixin, UserMixin
from tests.utils import captured_templates

from shop.orders.models import OrderModel
from shop.products.models import ProductModel
from shop.seed_db import (
    seed_brands,
    seed_categories,
    seed_products,
)

unittest.TestCase.maxDiff = None


class CartPageAnonymousUserTests(ClientRequestsMixin):
    def test_get_load_page(self):
        response = self.client.get(url_for('carts_blueprint.cart'))
        self.assertEqual(302, response.status_code)

        expected_url = url_for('users_blueprint.login', _external=True)
        self.assertTrue(str(response.location).startswith(expected_url))


class CartPageSuperuserTests(SuperuserMixin, CartPageAnonymousUserTests):
    def test_get_load_page(self):
        response = self.client.get(url_for('carts_blueprint.cart'))
        self.assertEqual(403, response.status_code)


class CartPageUserTests(UserMixin, CartPageAnonymousUserTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        seed_brands(n_brands=2)
        seed_categories(n_categories=2)

    def tearDown(self):
        super().tearDown()
        OrderModel.delete_all()
        ProductModel.delete_all()

    def fill_cart(self, n_products):
        seed_products(n_products)

        for product in ProductModel.get_all():
            post_data = {
                'add_to_cart-product_id': product.id,
                'add_to_cart-submit': True,
            }
            self.client.post(
                url_for('products_blueprint.products'),
                data=post_data,
            )

    def test_get_load_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('carts_blueprint.cart'))

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertListEqual([], context['items'])

    def test_get_non_empty_cart(self):
        n_products = randint(1, 10)
        self.fill_cart(n_products)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('carts_blueprint.cart'))

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertEqual(n_products, len(context['items']))

            expected_items = zip(ProductModel.get_all(), [1] * n_products)
            self.assertSetEqual(set(expected_items), set(context['items']))

    def test_post_clear_empty_cart(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'clear_cart-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertListEqual([], context['items'])

    def test_post_clear_non_empty_cart(self):
        n_products = randint(2, 10)
        self.fill_cart(n_products)

        with captured_templates(self.app) as templates:
            post_data = {
                'clear_cart-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)
            for pr in ProductModel.get_all():
                self.assertEqual(0, pr.reserved)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertListEqual([], context['items'])

    def test_post_place_order_on_empty_cart(self):
        post_data = {
            'place_order-submit': True,
        }
        response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

        self.assertEqual(409, response.status_code)
        self.assertListEqual([], OrderModel.get_all())

    def test_post_place_order_on_non_empty_cart(self):
        n_products = randint(2, 10)
        self.fill_cart(n_products)

        with captured_templates(self.app) as templates:
            post_data = {
                'place_order-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)
            for pr in ProductModel.get_all():
                self.assertEqual(1, pr.reserved)
            self.assertEqual(1, len(OrderModel.query.filter_by(user=self.user).all()))
            order = OrderModel.get(user=self.user)
            self.assertEqual(n_products, len(order.products.all()))

            expected_products_and_amounts = zip([1] * n_products, ProductModel.get_all())
            actual_products_and_amounts = [(item.amount, item.product) for item in order.products.all()]
            self.assertSetEqual(set(expected_products_and_amounts), set(actual_products_and_amounts))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertListEqual([], context['items'])

    def test_post_update_non_existent_product_amount(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'update_amount-product_id': randint(1, 10),
                'update_amount-new_amount': randint(1, 10),
                'update_amount-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(OrderModel.get_all()))
            self.assertEqual(0, len(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertListEqual([], context['items'])

            actual_error = str(context['update_amount_form']['product_id'].errors[0])
            self.assertEqual('Product with such id not exists.', actual_error)

    def test_post_increase_product_amount(self):
        self.fill_cart(1)
        product = ProductModel.get_random()

        with captured_templates(self.app) as templates:
            post_data = {
                'update_amount-product_id': product.id,
                'update_amount-new_amount': 2,
                'update_amount-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)
            product = ProductModel.get(id=product.id)
            self.assertIsNotNone(product)
            self.assertEqual(2, product.reserved)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertEqual(1, len(context['items']))

    def test_post_increase_too_much_product_amount(self):
        self.fill_cart(1)
        product = ProductModel.get_random()

        with captured_templates(self.app) as templates:
            post_data = {
                'update_amount-product_id': product.id,
                'update_amount-new_amount': product.amount + 1,
                'update_amount-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)
            product = ProductModel.get(id=product.id)
            self.assertIsNotNone(product)
            self.assertEqual(1, product.reserved)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertEqual(1, len(context['items']))

            actual_error = str(context['update_amount_form']['new_amount'].errors[0])
            self.assertEqual('Not enough product to add.', actual_error)

    def test_post_decrease_product_amount_to_zero(self):
        self.fill_cart(1)
        product = ProductModel.get_random()

        with captured_templates(self.app) as templates:
            post_data = {
                'update_amount-product_id': product.id,
                'update_amount-new_amount': 0,
                'update_amount-submit': True,
            }
            response = self.client.post(url_for('carts_blueprint.cart'), data=post_data)

            self.assertEqual(200, response.status_code)
            product = ProductModel.get(id=product.id)
            self.assertIsNotNone(product)
            self.assertEqual(0, product.reserved)
            self.assertEqual(0, len(OrderModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('carts/cart.html', template.name)
            self.assertEqual(0, len(context['items']))


if __name__ == "__main__":
    unittest.main()
