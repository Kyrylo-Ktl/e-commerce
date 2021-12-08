from random import randint
import unittest

from flask import url_for
from tests.mixins import ClientRequestsMixin, SuperuserMixin, UserMixin
from tests.utils import captured_templates

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

unittest.TestCase.maxDiff = None


class ProductsPageTests(ClientRequestsMixin):
    def tearDown(self):
        ProductModel.delete_all()
        BrandModel.delete_all()
        CategoryModel.delete_all()

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


class ProductsPageAnonymousUserTests(ClientRequestsMixin):
    def tearDown(self):
        ProductModel.delete_all()
        BrandModel.delete_all()
        CategoryModel.delete_all()

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


class ProductsPageUserTests(UserMixin, ProductsPageAnonymousUserTests):
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


class ProductsPageSuperuserTests(SuperuserMixin, ProductsPageAnonymousUserTests):
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


class ProductDetailPageAnonymousUserTests(ClientRequestsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)

    def tearDown(self):
        ProductModel.delete_all()

    def test_get_page_for_non_existent_product(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.product_detail',
                product_id=randint(1, 10),
            ))

            self.assertEqual(404, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/404.html', template.name)

    def test_get_page_for_existing_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.product_detail',
                product_id=product.id,
            ))

            self.assertEqual(200, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/product_detail.html', template.name)
            self.assertEqual(product, context['product'])

    def test_post_add_product_to_cart(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_card-product_id': product.id,
                'add_to_card-amount_to_add': randint(1, product.amount),
                'add_to_card-submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.product_detail',
                product_id=product.id,
            ), data=post_data)

            self.assertEqual(403, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)

    def test_post_delete_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_product-product_id': product.id,
                'delete_product-submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.product_detail',
                product_id=product.id,
            ), data=post_data)

            self.assertEqual(403, response.status_code)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)


class ProductDetailPageUserTests(UserMixin, ProductDetailPageAnonymousUserTests):
    def test_post_add_product_to_cart(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = randint(1, product.amount)

        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_card-product_id': product.id,
                'add_to_card-amount_to_add': amount_to_add,
                'add_to_card-submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.product_detail',
                product_id=product.id,
            ), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(amount_to_add, product.reserved)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/product_detail.html', template.name)
            self.assertEqual(product, context['product'])

    def test_post_add_product_to_cart_with_too_big_amount(self):
        product = ProductModel.create(**get_random_product_data())
        amount_to_add = product.amount + randint(1, 10)

        with captured_templates(self.app) as templates:
            post_data = {
                'add_to_card-product_id': product.id,
                'add_to_card-amount_to_add': amount_to_add,
                'add_to_card-submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.product_detail',
                product_id=product.id,
            ), data=post_data)

            self.assertEqual(200, response.status_code)
            self.assertEqual(0, product.reserved)

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/product_detail.html', template.name)
            self.assertEqual(product, context['product'])

            expected_error = str(context['add_to_cart_form'].errors['amount_to_add'][0])
            self.assertEqual('Not enough product to add.', expected_error)


class ProductDetailPageSuperuserTests(SuperuserMixin, ProductDetailPageAnonymousUserTests):
    def test_post_delete_product(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'delete_product-product_id': product.id,
                'delete_product-submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.product_detail',
                product_id=product.id,
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertIsNone(ProductModel.get(id=product.id))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)
            self.assertEqual([], context['products'])


class CreateBrandPageAnonymousUserTests(ClientRequestsMixin):
    def tearDown(self):
        BrandModel.delete_all()

    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.create_brand'
            ), follow_redirects=True)

            self.assertEqual(403, response.status_code)
            self.assertSetEqual(set(), set(BrandModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)

    def test_post_create_brand(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'brand_name': fake.word(),
                'submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.create_brand'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(403, response.status_code)
            self.assertSetEqual(set(), set(BrandModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)


class CreateBrandPageUserTests(UserMixin, CreateBrandPageAnonymousUserTests):
    pass


class CreateBrandPageSuperuserTests(SuperuserMixin, CreateBrandPageAnonymousUserTests):
    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.create_brand'
            ), follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual(set(), set(BrandModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_brand.html', template.name)

    def test_post_create_brand(self):
        random_name = fake.word()

        with captured_templates(self.app) as templates:
            post_data = {
                'brand_name': random_name,
                'submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.create_brand'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual({BrandModel.get(name=random_name)}, set(BrandModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)
            self.assertSetEqual({BrandModel.get(name=random_name)}, set(context['brands']))

    def test_post_create_brand_with_existing_title(self):
        brand = BrandModel.create(**get_random_brand_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'brand_name': brand.name,
                'submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.create_brand'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual({brand}, set(BrandModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_brand.html', template.name)

            actual_error = str(context['form'].errors['brand_name'][0])
            self.assertEqual('Brand with such name already exists.', actual_error)


class CreateCategoryPageAnonymousUserTests(ClientRequestsMixin):
    def tearDown(self):
        CategoryModel.delete_all()

    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.create_category'
            ), follow_redirects=True)

            self.assertEqual(403, response.status_code)
            self.assertSetEqual(set(), set(CategoryModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)

    def test_post_create_category(self):
        with captured_templates(self.app) as templates:
            post_data = {
                'category_name': fake.word(),
                'submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.create_category'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(403, response.status_code)
            self.assertSetEqual(set(), set(CategoryModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)


class CreateCategoryPageUserTests(UserMixin, CreateCategoryPageAnonymousUserTests):
    pass


class CreateCategoryPageSuperuserTests(SuperuserMixin, CreateCategoryPageAnonymousUserTests):
    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.create_category'
            ), follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual(set(), set(CategoryModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_category.html', template.name)

    def test_post_create_category(self):
        random_name = fake.word()

        with captured_templates(self.app) as templates:
            post_data = {
                'category_name': random_name,
                'submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.create_category'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual({CategoryModel.get(name=random_name)}, set(CategoryModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/products_list.html', template.name)
            self.assertSetEqual({CategoryModel.get(name=random_name)}, set(context['categories']))

    def test_post_create_category_with_existing_title(self):
        category = CategoryModel.create(**get_random_category_data())

        with captured_templates(self.app) as templates:
            post_data = {
                'category_name': category.name,
                'submit': True,
            }
            response = self.client.post(url_for(
                'products_blueprint.create_category'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual({category}, set(CategoryModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_category.html', template.name)

            actual_error = str(context['form'].errors['category_name'][0])
            self.assertEqual('Category with such name already exists.', actual_error)


class CreateProductPageAnonymousUserTests(ClientRequestsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)

    def tearDown(self):
        ProductModel.delete_all()

    @staticmethod
    def random_post_data():
        post_data = get_random_product_data()
        post_data.pop('image_file')
        post_data['brand'] = post_data['brand'].name
        post_data['category'] = post_data['category'].name
        post_data['picture'] = None
        post_data['submit'] = True
        return post_data

    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.create_product'
            ), follow_redirects=True)

            self.assertEqual(403, response.status_code)
            self.assertSetEqual(set(), set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)

    def test_post_create_product(self):
        with captured_templates(self.app) as templates:
            post_data = CreateProductPageAnonymousUserTests.random_post_data()
            response = self.client.post(url_for(
                'products_blueprint.create_product'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(403, response.status_code)
            self.assertSetEqual(set(), set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('errors/403.html', template.name)


class CreateProductPageUserTests(UserMixin, CreateProductPageAnonymousUserTests):
    pass


class CreateProductPageSuperuserTests(SuperuserMixin, CreateProductPageAnonymousUserTests):
    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'products_blueprint.create_product'
            ), follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual(set(), set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_product.html', template.name)

    def test_post_create_product(self):
        with captured_templates(self.app) as templates:
            post_data = CreateProductPageAnonymousUserTests.random_post_data()
            response = self.client.post(url_for(
                'products_blueprint.create_product'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)

            product = ProductModel.get(name=post_data['name'])
            self.assertIsNotNone(product)
            self.assertSetEqual({product}, set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/product_detail.html', template.name)
            self.assertEqual(product, context['product'])

    def test_post_create_product_with_existing_title(self):
        product = ProductModel.create(**get_random_product_data())

        with captured_templates(self.app) as templates:
            post_data = CreateProductPageAnonymousUserTests.random_post_data()
            post_data['name'] = product.name

            response = self.client.post(url_for(
                'products_blueprint.create_product'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual({product}, set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_product.html', template.name)

            actual_error = str(context['form'].errors['name'][0])
            self.assertEqual('Product with such name already exists.', actual_error)

    def test_post_create_product_with_negative_amount(self):
        with captured_templates(self.app) as templates:
            post_data = CreateProductPageAnonymousUserTests.random_post_data()
            post_data['amount'] = -randint(1, 10)

            response = self.client.post(url_for(
                'products_blueprint.create_product'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual(set(), set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_product.html', template.name)

            actual_error = str(context['form'].errors['amount'][0])
            self.assertEqual('Number must be between 0 and 1000000.', actual_error)

    def test_post_create_product_with_negative_price(self):
        with captured_templates(self.app) as templates:
            post_data = CreateProductPageAnonymousUserTests.random_post_data()
            post_data['price'] = -randint(1, 10)

            response = self.client.post(url_for(
                'products_blueprint.create_product'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual(set(), set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_product.html', template.name)

            actual_error = str(context['form'].errors['price'][0])
            self.assertEqual('Number must be between 0.01 and 1000000.', actual_error)

    def test_post_create_product_with_invalid_discount(self):
        with captured_templates(self.app) as templates:
            post_data = CreateProductPageAnonymousUserTests.random_post_data()
            post_data['discount'] = -randint(1, 10)

            response = self.client.post(url_for(
                'products_blueprint.create_product'
            ), data=post_data, follow_redirects=True)

            self.assertEqual(200, response.status_code)
            self.assertSetEqual(set(), set(ProductModel.get_all()))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('products/create_product.html', template.name)

            actual_error = str(context['form'].errors['discount'][0])
            self.assertEqual('Number must be between 0 and 99.', actual_error)


if __name__ == "__main__":
    unittest.main()
