import os
from random import randint
import unittest

from sqlalchemy.exc import IntegrityError

from shop import create_app
from shop.db import db
from shop.orders.models import OrderModel
from shop.products.models import ProductModel
from shop.seed_db import (
    fake,
    get_random_product_data,
    get_random_user_data,
    seed_brands,
    seed_categories,
    seed_products, seed_orders, seed_users
)
from shop.users.models import UserModel


class ProductModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.app_context().push()
        db.create_all()
        seed_brands(n_brands=10)
        seed_categories(n_categories=10)
        cls.N_PRODUCTS = 5

    @classmethod
    def tearDownClass(cls):
        db.reflect()
        db.drop_all()

    def setUp(self):
        seed_products(n_products=self.N_PRODUCTS)

    def tearDown(self):
        for pr in ProductModel.get_all():
            pr.delete()

    def test_discount_price_calculation(self):
        random_product = ProductModel.get_random()

        expected_price = round(random_product.price * (1 - random_product.discount / 100), 2)
        self.assertTrue(abs(expected_price - random_product.discount_price) <= 1e-3)

    def test_available_amount_calculation(self):
        random_product = ProductModel.get_random()

        expected_available = random_product.amount - random_product.reserved
        self.assertEqual(expected_available, random_product.available)

    def test_create_product_with_negative_amount(self):
        product_data = get_random_product_data(create_image=False)
        product_data['amount'] = -randint(1, 25)

        with self.assertRaises(IntegrityError) as context:
            ProductModel.create(**product_data)

        self.assertTrue('product_non_negative_amount_constraint' in str(context.exception))
        self.assertEqual(len(ProductModel.get_all()), self.N_PRODUCTS)

    def test_create_product_with_too_big_reserved_amount(self):
        product_data = get_random_product_data(create_image=False)
        product_data['reserved'] = product_data['amount'] + randint(1, 10)

        with self.assertRaises(IntegrityError) as context:
            ProductModel.create(**product_data)

        self.assertTrue('product_valid_reserved_amount_constraint' in str(context.exception))
        self.assertEqual(len(ProductModel.get_all()), self.N_PRODUCTS)

    def test_create_product_with_too_big_discount(self):
        product_data = get_random_product_data(create_image=False)
        product_data['discount'] = randint(100, 200)

        with self.assertRaises(IntegrityError) as context:
            ProductModel.create(**product_data)

        self.assertTrue('valid_product_discount_constraint' in str(context.exception))
        self.assertEqual(len(ProductModel.get_all()), self.N_PRODUCTS)

    def test_create_product_with_too_small_discount(self):
        product_data = get_random_product_data(create_image=False)
        product_data['discount'] = -randint(1, 100)

        with self.assertRaises(IntegrityError) as context:
            ProductModel.create(**product_data)

        self.assertTrue('valid_product_discount_constraint' in str(context.exception))
        self.assertEqual(len(ProductModel.get_all()), self.N_PRODUCTS)

    def test_is_product_image_deleted_with_product(self):
        product_data = get_random_product_data(create_image=True)
        product = ProductModel.create(**product_data)

        self.assertNotEqual(product.image_file, ProductModel.DEFAULT_IMAGE)

        full_path = os.path.join(self.app.root_path, 'static', product.image_file)
        self.assertTrue(os.path.isfile(full_path))
        product.delete()
        self.assertFalse(os.path.isfile(full_path))

    def test_is_product_image_deleted_after_updating(self):
        product_data = get_random_product_data(create_image=True)
        product = ProductModel.create(**product_data)

        self.assertNotEqual(product.image_file, ProductModel.DEFAULT_IMAGE)

        full_path = os.path.join(self.app.root_path, 'static', product.image_file)
        self.assertTrue(os.path.isfile(full_path))
        product.update_image_file(ProductModel.DEFAULT_IMAGE)
        self.assertFalse(os.path.isfile(full_path))


class UserModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.app_context().push()
        db.create_all()
        cls.N_USERS = 10

    @classmethod
    def tearDownClass(cls):
        db.reflect()
        db.drop_all()

    def test_password_hashing(self):
        user_data = get_random_user_data(create_image=True)
        plaintext_password = fake.word()
        user_data['password'] = plaintext_password
        user = UserModel.create(**user_data)

        self.assertNotEqual(user.password, plaintext_password)
        self.assertTrue(user.check_password(plaintext_password))

    def test_change_password(self):
        user_data = get_random_user_data(create_image=True)
        user = UserModel.create(**user_data)

        plaintext_password = fake.word()
        user.password = plaintext_password
        user.save()

        self.assertNotEqual(user.password, plaintext_password)
        self.assertTrue(user.check_password(plaintext_password))

    def test_is_product_image_deleted_with_user(self):
        user_data = get_random_user_data(create_image=True)
        user = UserModel.create(**user_data)

        self.assertNotEqual(user.image_file, UserModel.DEFAULT_IMAGE)

        full_path = os.path.join(self.app.root_path, 'static', user.image_file)
        self.assertTrue(os.path.isfile(full_path))
        user.delete()
        self.assertFalse(os.path.isfile(full_path))

    def test_is_product_image_deleted_after_updating(self):
        user_data = get_random_user_data(create_image=True)
        user = UserModel.create(**user_data)

        self.assertNotEqual(user.image_file, UserModel.DEFAULT_IMAGE)

        full_path = os.path.join(self.app.root_path, 'static', user.image_file)
        self.assertTrue(os.path.isfile(full_path))
        user.update_image_file(UserModel.DEFAULT_IMAGE)
        self.assertFalse(os.path.isfile(full_path))


class OrderModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.app_context().push()
        db.create_all()
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=10)
        seed_users(n_users=1)
        cls.N_ORDERS = 1

    @classmethod
    def tearDownClass(cls):
        db.reflect()
        db.drop_all()

    def setUp(self):
        seed_orders(
            n_orders=self.N_ORDERS,
            max_products=10,
            max_product_amount=5,
        )

    def tearDown(self):
        for order in OrderModel.get_all():
            order.delete()

    def test_total_items_calculation(self):
        random_order = OrderModel.get_random()

        expected_amount = sum(item.amount for item in random_order.products)
        self.assertEqual(expected_amount, random_order.total_items)

    def test_total_sum_calculation(self):
        random_order = OrderModel.get_random()

        expected_sum = sum(item.amount * item.product.discount_price for item in random_order.products)
        expected_sum = round(expected_sum, 2)
        self.assertTrue(abs(expected_sum - random_order.total_sum) <= 1e-3)

    def test_add_product(self):
        order = OrderModel.create(user=UserModel.get_random())

        self.assertEqual(order.total_items, 0)
        self.assertEqual(order.total_sum, 0)

        product = ProductModel.get_random()
        amount_to_add = randint(1, product.available)
        order.add_product(product, amount_to_add)

        self.assertEqual(order.total_items, amount_to_add)
        expected_total = round(product.discount_price * amount_to_add, 2)
        self.assertTrue(abs(order.total_sum - expected_total) <= 1e-3)

    def test_complete_order(self):
        random_order = OrderModel.create(user=UserModel.get_random())

        self.assertEqual(random_order.is_completed, False)

        random_product = ProductModel.create(**get_random_product_data())
        self.assertEqual(random_product.reserved, 0)

        available_amount = random_product.amount
        amount_to_add = randint(1, available_amount)
        random_product.reserved += amount_to_add
        random_product.save()

        random_order.add_product(random_product, amount=amount_to_add)
        random_order.complete()

        self.assertEqual(random_order.is_completed, True)
        self.assertEqual(available_amount - amount_to_add, random_product.amount)
        self.assertEqual(random_product.reserved, 0)


if __name__ == "__main__":
    unittest.main()
