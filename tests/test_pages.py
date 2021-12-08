from random import randint
import secrets
import unittest

from flask import url_for
from tests.utils import captured_templates
from tests.utils import login, logout

from shop import create_app
from shop.db import db
from shop.products.models import BrandModel, CategoryModel, ProductModel
from shop.seed_db import (
    fake,
    get_random_brand_data,
    get_random_category_data,
    get_random_product_data,
    seed_brands,
    seed_categories,
    seed_products,
)
from shop.users.models import UserModel

unittest.TestCase.maxDiff = None


class ProductsPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.app_context().push()

        cls._ctx = cls.app.test_request_context()
        cls._ctx.push()

        cls.client = cls.app.test_client()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def setUp(self):
        pass

    def tearDown(self):
        for pr in ProductModel.get_all():
            pr.delete()
        for br in BrandModel.get_all():
            br.delete()
        for ct in CategoryModel.get_all():
            ct.delete()

    def test_get_page_with_no_products(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products'))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)

            template, context = templates[0]
            self.assertEqual(template.name, 'products/products_list.html')
            self.assertEqual(context['page'], 1)
            self.assertListEqual(context['brands'], [])
            self.assertListEqual(context['categories'], [])
            self.assertListEqual(context['products'], [])

            self.assertEqual(context['kwargs']['brand_name'], None)
            self.assertEqual(context['kwargs']['category_name'], None)

    def test_get_page_with_products(self):
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=ProductModel.PAGINATE_BY)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products'))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)

            template, context = templates[0]
            self.assertEqual(template.name, 'products/products_list.html')
            self.assertEqual(context['page'], 1)
            self.assertListEqual(context['brands'], BrandModel.get_all())
            self.assertListEqual(context['categories'], CategoryModel.get_all())
            self.assertListEqual(context['products'], ProductModel.get_all())

            self.assertEqual(context['kwargs']['brand_name'], None)
            self.assertEqual(context['kwargs']['category_name'], None)

    def test_page_get_products_for_brand(self):
        seed_brands(n_brands=2)
        seed_categories(n_categories=5)
        seed_products(n_products=ProductModel.PAGINATE_BY)
        brand = BrandModel.get_random()

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', brand_name=brand.name))

            self.assertEqual(response.status_code, 200)
            template, context = templates[0]

            self.assertEqual(context['page'], 1)
            self.assertListEqual(context['brands'], BrandModel.get_all())
            self.assertListEqual(context['categories'], CategoryModel.get_all())

            expected_products = ProductModel.query.filter_by(brand=brand).all()
            actual_products = context['products']
            self.assertSetEqual(set(expected_products), set(actual_products))

            self.assertEqual(context['kwargs']['brand_name'], brand.name)
            self.assertEqual(context['kwargs']['category_name'], None)

    def test_page_get_products_for_category(self):
        seed_brands(n_brands=5)
        seed_categories(n_categories=2)
        seed_products(n_products=ProductModel.PAGINATE_BY)
        category = CategoryModel.get_random()

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', category_name=category.name))

            self.assertEqual(response.status_code, 200)
            template, context = templates[0]

            self.assertEqual(context['page'], 1)
            self.assertListEqual(context['brands'], BrandModel.get_all())
            self.assertListEqual(context['categories'], CategoryModel.get_all())

            expected_products = ProductModel.query.filter_by(category=category).all()
            actual_products = context['products']
            self.assertSetEqual(set(expected_products), set(actual_products))

            self.assertEqual(context['kwargs']['brand_name'], None)
            self.assertEqual(context['kwargs']['category_name'], category.name)

    def test_get_valid_random_page(self):
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=10 * ProductModel.PAGINATE_BY)
        random_page = randint(2, 10)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=random_page))

            self.assertEqual(200, response.status_code)

            template, context = templates[0]
            self.assertEqual(ProductModel.PAGINATE_BY, len(context['products']))
            self.assertEqual(random_page, context['page'])
            self.assertEqual(10, context['pagination'].pages)

            self.assertEqual(context['kwargs']['brand_name'], None)
            self.assertEqual(context['kwargs']['category_name'], None)

    def test_get_next_page_with_brand_filter(self):
        seed_categories(n_categories=5)
        seed_brands(n_brands=2)
        brand = BrandModel.get_random()
        seed_products(n_products=10 * ProductModel.PAGINATE_BY)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=2, brand_name=brand.name))

            self.assertEqual(200, response.status_code)

            template, context = templates[0]
            self.assertEqual(ProductModel.PAGINATE_BY, len(context['products']))
            self.assertEqual(2, context['page'])
            self.assertNotEqual(context['pagination'].pages, 10)
            self.assertTrue(all(pr.brand == brand for pr in context['products']))

            self.assertEqual(context['kwargs']['brand_name'], brand.name)
            self.assertEqual(context['kwargs']['category_name'], None)

    def test_get_next_page_with_category_filter(self):
        seed_categories(n_categories=2)
        seed_brands(n_brands=5)
        category = CategoryModel.get_random()
        seed_products(n_products=10 * ProductModel.PAGINATE_BY)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=2, category_name=category.name))

            self.assertEqual(200, response.status_code)

            template, context = templates[0]
            self.assertEqual(ProductModel.PAGINATE_BY, len(context['products']))
            self.assertEqual(2, context['page'])
            self.assertNotEqual(context['pagination'].pages, 10)
            self.assertTrue(all(pr.category == category for pr in context['products']))

            self.assertEqual(context['kwargs']['brand_name'], None)
            self.assertEqual(context['kwargs']['category_name'], category.name)

    def test_get_too_big_page_with_no_products(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=randint(2, 10)))

            self.assertEqual(404, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('errors/404.html', template.name)

    def test_get_too_big_page_with_products(self):
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=ProductModel.PAGINATE_BY)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=randint(2, 10)))

            self.assertEqual(response.status_code, 404)
            self.assertEqual(len(templates), 1)

            template, context = templates[0]
            self.assertEqual(template.name, 'errors/404.html')

    def test_get_negative_page_with_no_products(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=-randint(0, 10)))

            self.assertEqual(404, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('errors/404.html', template.name)

    def test_get_negative_page_with_products(self):
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=ProductModel.PAGINATE_BY)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('products_blueprint.products', page=-randint(0, 10)))

            self.assertEqual(response.status_code, 404)
            self.assertEqual(len(templates), 1)

            template, context = templates[0]
            self.assertEqual(template.name, 'errors/404.html')


class ProductsPageAnonymousUserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.app_context().push()

        cls._ctx = cls.app.test_request_context()
        cls._ctx.push()

        cls.client = cls.app.test_client()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.reflect()
        db.drop_all()

    def tearDown(self):
        for pr in ProductModel.get_all():
            pr.delete()
        for br in BrandModel.get_all():
            br.delete()
        for ct in CategoryModel.get_all():
            ct.delete()

    def test_delete_non_existing_product(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'delete_product-product_id': randint(1, 10),
                'delete_product-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)

            actual_error_message = str(context['delete_product_form'].errors['product_id'][0])
            self.assertEqual('Product with such id not exists.', actual_error_message)

    def test_delete_existing_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_product-product_id': product.id,
                'delete_product-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(403, response.status_code)
            self.assertEqual(1, len(templates))

            template, _ = templates[0]
            self.assertEqual('errors/403.html', template.name)

            self.assertEqual(product, ProductModel.get(id=product.id))

    def test_delete_non_existing_category(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'delete_category-category_id': randint(1, 10),
                'delete_category-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)

            actual_error_message = str(context['delete_category_form'].errors['category_id'][0])
            self.assertEqual('Category with such id not exists.', actual_error_message)

    def test_delete_existing_category(self):
        category = CategoryModel.create(**get_random_category_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_category-category_id': category.id,
                'delete_category-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(403, response.status_code)
            self.assertEqual(1, len(templates))

            template, _ = templates[0]
            self.assertEqual('errors/403.html', template.name)

            self.assertEqual(category, CategoryModel.get(id=category.id))

    def test_delete_non_existing_brand(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'delete_brand-brand_id': randint(1, 10),
                'delete_brand-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)

            actual_error_message = str(context['delete_brand_form'].errors['brand_id'][0])
            self.assertEqual('Brand with such id not exists.', actual_error_message)

    def test_delete_existing_brand(self):
        brand = BrandModel.create(**get_random_brand_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_brand-brand_id': brand.id,
                'delete_brand-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(403, response.status_code)
            self.assertEqual(1, len(templates))

            template, _ = templates[0]
            self.assertEqual('errors/403.html', template.name)

            self.assertEqual(brand, BrandModel.get(id=brand.id))

    def test_add_to_cart_non_existent_product(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_cart-product_id': randint(1, 10),
                'add_to_cart-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)

            actual_error_message = str(context['add_to_cart_form'].errors['product_id'][0])
            self.assertEqual('Product with such id not exists.', actual_error_message)

    def test_add_to_cart_existing_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_cart-product_id': product.id,
                'add_to_cart-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(403, response.status_code)
            self.assertEqual(1, len(templates))

            template, _ = templates[0]
            self.assertEqual('errors/403.html', template.name)

    def test_add_to_cart_existing_product_with_no_available(self):
        product = ProductModel.create(**get_random_product_data())
        product.reserved = product.amount
        product.save()

        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_cart-product_id': product.id,
                'add_to_cart-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)

            actual_error_message = str(context['add_to_cart_form'].errors['product_id'][0])
            self.assertEqual('Not enough product to add.', actual_error_message)


class ProductsPageUserTests(ProductsPageAnonymousUserTests):
    @classmethod
    def setUpClass(cls):
        ProductsPageAnonymousUserTests.setUpClass()
        cls.user_username = fake.name()
        cls.user_password = secrets.token_hex(16)
        cls.user_email = fake.email()

        cls.user = UserModel.create(
            email=cls.user_email,
            username=cls.user_username,
            password=cls.user_password,
            confirmed=True,
        )

    def setUp(self):
        login(self.client, self.user_email, self.user_password)

    def tearDown(self):
        logout(self.client)
        super(ProductsPageUserTests, self).tearDown()

    def test_add_to_cart_existing_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_cart-product_id': product.id,
                'add_to_cart-submit': True,
            }
            response = self.client.post(url_for('products_blueprint.products'), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, _ = templates[0]
            self.assertEqual('products/products_list.html', template.name)

            self.assertEqual(1, product.reserved)


class ProductsPageSuperuserTests(ProductsPageAnonymousUserTests):
    @classmethod
    def setUpClass(cls):
        ProductsPageAnonymousUserTests.setUpClass()
        cls.admin_username = fake.name()
        cls.admin_password = secrets.token_hex(16)
        cls.admin_email = fake.email()

        cls.admin = UserModel.create(
            email=cls.admin_email,
            username=cls.admin_username,
            password=cls.admin_password,
            confirmed=True,
            is_superuser=True,
        )

    def setUp(self):
        login(self.client, self.admin_email, self.admin_password)

    def tearDown(self):
        logout(self.client)
        super(ProductsPageSuperuserTests, self).tearDown()

    def test_delete_existing_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_product-product_id': product.id,
                'delete_product-submit': True,
            }
            response = self.client.post(
                url_for('products_blueprint.products'),
                data=post_data,
                follow_redirects=True,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(ProductModel.get_all(), [])

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual([], context['products'])
            self.assertEqual('products/products_list.html', template.name)

    def test_delete_existing_brand(self):
        brand = BrandModel.create(**get_random_brand_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_brand-brand_id': brand.id,
                'delete_brand-submit': True,
            }
            response = self.client.post(
                url_for('products_blueprint.products'),
                data=post_data,
                follow_redirects=True,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(BrandModel.get_all(), [])

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual([], context['brands'])
            self.assertEqual('products/products_list.html', template.name)

    def test_delete_existing_category(self):
        category = CategoryModel.create(**get_random_category_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_category-category_id': category.id,
                'delete_category-submit': True,
            }
            response = self.client.post(
                url_for('products_blueprint.products'),
                data=post_data,
                follow_redirects=True,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(CategoryModel.get_all(), [])

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual([], context['categories'])
            self.assertEqual('products/products_list.html', template.name)


if __name__ == "__main__":
    unittest.main()
