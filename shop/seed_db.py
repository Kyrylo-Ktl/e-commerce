"""
Module with functions for filling the database with random data
"""
import os
from random import randint
import secrets

from faker import Faker
from flask import current_app
from sqlalchemy.sql.expression import func

from shop.products.helpers import create_random_image
from shop.products.models import BrandModel, CategoryModel, ProductModel
from shop.users.models import UserModel
from shop.orders.models import OrderModel


def seed_brands(n_brands: int = 10) -> None:
    fake = Faker()
    for _ in range(n_brands):
        BrandModel.create(
            name=' '.join(fake.words(3)).capitalize(),
        )


def seed_categories(n_categories: int = 10) -> None:
    fake = Faker()
    for _ in range(n_categories):
        CategoryModel.create(
            name=' '.join(fake.words(3)).capitalize(),
        )


def seed_products(n_products: int = 10) -> None:
    fake = Faker()
    for _ in range(n_products):
        random_hex = secrets.token_hex(8)

        image_file = os.path.join(
            ProductModel.IMAGE_DIR,
            random_hex + '.png',
        )
        image_path = os.path.join(
            current_app.root_path,
            'static',
            image_file,
        )
        create_random_image(image_path, (250, 250))

        ProductModel.create(
            name=' '.join(fake.words(4)).capitalize(),
            short_description=fake.text(200),
            full_description=fake.text(1000),
            price=randint(100, 1000) / 10,
            amount=randint(1, 25),
            discount=int(randint(1, 10) > 6) * randint(10, 30),
            brand_id=BrandModel.query.order_by(func.random()).first().id,
            category_id=CategoryModel.query.order_by(func.random()).first().id,
            image_file=image_file,
        )


def seed_admin():
    UserModel(
        username='admin',
        email='admin@admin.admin',
        password='admin',
        is_superuser=True,
        confirmed=True,
    )


def seed_users(n_users: int = 10) -> None:
    fake = Faker()
    for _ in range(n_users):
        UserModel(
            username=f'{fake.last_name()}_{fake.first_name().lower()}',
            email=fake.email(),
            password='1234',
            confirmed=True,
        )


def seed_orders(n_orders: int = 25) -> None:
    for _ in range(n_orders):
        random_user = UserModel.query.order_by(func.random()).first()
        order = OrderModel.create(user=random_user)

        for product in ProductModel.query.order_by(func.random()).all()[:randint(1, 10)]:
            if product.available:
                amount_to_add = randint(1, product.available)
                product.reserved += amount_to_add
                product.save()
                order.add_product(product, amount=amount_to_add)

        if randint(1, 10) > 6:
            order.complete()
