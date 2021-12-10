"""Module with functions for filling the database with random data"""

import os
from random import randint
import secrets

from faker import Faker
from flask import current_app
from sqlalchemy.sql.expression import func

from shop.core.utils import create_random_image
from shop.orders.models import OrderModel
from shop.products.models import BrandModel, CategoryModel, ProductModel
from shop.users.models import UserModel

fake = Faker()


def get_random_category_data():
    random_data = {
        'name': ' '.join(fake.words(3)).capitalize(),
    }
    return random_data


def get_random_brand_data():
    random_data = {
        'name': ' '.join(fake.words(3)).capitalize(),
    }
    return random_data


def get_random_product_data(create_image: bool = False):
    image_file = ProductModel.DEFAULT_IMAGE

    if create_image:
        random_hex = secrets.token_hex(8)

        image_file = os.path.join(ProductModel.IMAGE_DIR, random_hex + '.png')
        image_path = os.path.join(current_app.root_path, 'static', image_file)
        create_random_image(image_path, (250, 250))

    random_data = {
        'name': ' '.join(fake.words(4)).capitalize(),
        'short_description': fake.text(200),
        'full_description': fake.text(1000),
        'price': randint(100, 1000) / 10,
        'amount': randint(1, 25),
        'discount': int(randint(1, 10) > 6) * randint(10, 30),
        'brand': BrandModel.get_random(),
        'category': CategoryModel.get_random(),
        'image_file': image_file,
    }
    return random_data


def get_random_user_data(is_confirmed: bool = False, create_image: bool = False):
    image_file = UserModel.DEFAULT_IMAGE

    if create_image:
        random_hex = secrets.token_hex(8)

        image_file = os.path.join(UserModel.IMAGE_DIR, random_hex + '.png')
        image_path = os.path.join(current_app.root_path, 'static', image_file)
        create_random_image(image_path, (250, 250))

    random_data = {
        'username': f'{fake.last_name()}_{fake.first_name().lower()}',
        'email': fake.email(),
        'password': '1234',
        'confirmed': is_confirmed,
        'image_file': image_file,
    }
    return random_data


def seed_categories(n_categories: int = 10):
    for _ in range(n_categories):
        CategoryModel.create(
            **get_random_category_data(),
        )


def seed_brands(n_brands: int = 10):
    for _ in range(n_brands):
        BrandModel.create(
            **get_random_brand_data(),
        )


def seed_products(n_products: int = 10, with_images: bool = True):
    for _ in range(n_products):
        ProductModel.create(
            **get_random_product_data(create_image=with_images),
        )


def seed_admin():
    UserModel(
        username='admin',
        email='admin@admin.admin',
        password='admin',
        is_superuser=True,
        confirmed=True,
    )


def seed_users(n_users: int = 10):
    for _ in range(n_users):
        UserModel(
            **get_random_user_data(is_confirmed=True),
        )


def seed_orders(n_orders: int = 25, max_products: int = 10, max_product_amount: int = 5) -> None:
    for _ in range(n_orders):
        order = OrderModel.create(user=UserModel.get_random())

        available_products = ProductModel.query.filter(ProductModel.available > 0)
        for product in available_products.order_by(func.random()).limit(randint(1, max_products)).all():
            amount_to_add = randint(1, min(max_product_amount, product.available))
            product.reserved += amount_to_add
            product.save()
            order.add_product(product, amount=amount_to_add)

        if randint(1, 10) > 6:
            order.complete()


def clear_all():
    OrderModel.delete_all()
    ProductModel.delete_all()
    UserModel.delete_all()
    BrandModel.delete_all()
    CategoryModel.delete_all()
