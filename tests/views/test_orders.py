import unittest

from flask import url_for
from tests.mixins import ClientRequestsMixin, SuperuserMixin, UserMixin
from tests.utils import captured_templates

from shop.orders.models import OrderModel
from shop.seed_db import (
    seed_brands,
    seed_categories,
    seed_orders,
    seed_products,
    seed_users
)

unittest.TestCase.maxDiff = None


class OrdersListAnonymousUserPageTests(ClientRequestsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=100)
        seed_users(n_users=10)
        seed_orders(n_orders=OrderModel.PAGINATE_BY, max_products=3)

    def test_get_load_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'orders_blueprint.orders_list'
            ), follow_redirects=True)

            self.assertEqual(403, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)


class UpdateProductPageUserTests(UserMixin, OrdersListAnonymousUserPageTests):
    pass


class UpdateProductPageSuperuserTests(SuperuserMixin, OrdersListAnonymousUserPageTests):
    def test_get_load_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'orders_blueprint.orders_list'
            ), follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('orders/orders_list.html', template.name)

            expected_orders = set(OrderModel.get_all())
            actual_orders = set(context['orders'])
            self.assertSetEqual(expected_orders, actual_orders)
            self.assertIsNone(context['kwargs']['completed'])

    def test_get_completed_orders(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'orders_blueprint.orders_list',
                completed=True,
            ), follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('orders/orders_list.html', template.name)

            self.assertTrue(all(order.is_completed for order in context['orders']))
            self.assertEqual('True', context['kwargs']['completed'])

    def test_get_non_completed_orders(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'orders_blueprint.orders_list',
                completed=False,
            ), follow_redirects=True)

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('orders/orders_list.html', template.name)

            self.assertFalse(any(order.is_completed for order in context['orders']))
            self.assertEqual('False', context['kwargs']['completed'])

    def test_post_complete_order(self):
        order = OrderModel.get_random()

        with captured_templates(self.app) as templates:
            post_data = {
                'order_id': order.id,
            }
            response = self.client.post(url_for(
                'orders_blueprint.orders_list'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertTrue(order.is_completed)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('orders/orders_list.html', template.name)
            self.assertIsNone(context['kwargs']['completed'])


if __name__ == "__main__":
    unittest.main()
