"""Module with custom validators for form fields"""

from wtforms.validators import ValidationError

from shop.orders.models import OrderModel
from shop.products.models import BrandModel, CategoryModel, ProductModel
from shop.users.models import UserModel


def user_validator(db_field, must_exist=True, error_msg=None):
    def _user_validator(_, field):
        product = UserModel.get(**{db_field: field.data})
        if product is None and must_exist:
            raise ValidationError(error_msg or f'User with such {db_field} not exists.')
        if product is not None and not must_exist:
            raise ValidationError(error_msg or f'User with such {db_field} already exists.')
    return _user_validator


def product_validator(db_field, must_exist=True, error_msg=None):
    def _product_validator(_, field):
        product = ProductModel.get(**{db_field: field.data})
        if product is None and must_exist:
            raise ValidationError(error_msg or f'Product with such {db_field} not exists.')
        if product is not None and not must_exist:
            raise ValidationError(error_msg or f'Product with such {db_field} already exists.')
    return _product_validator


def brand_validator(db_field, must_exist=True, error_msg=None):
    def _brand_validator(_, field):
        brand = BrandModel.get(**{db_field: field.data})
        if brand is None and must_exist:
            raise ValidationError(error_msg or f'Brand with such {db_field} not exists.')
        if brand is not None and not must_exist:
            raise ValidationError(error_msg or f'Brand with such {db_field} already exists.')
    return _brand_validator


def category_validator(db_field, must_exist=True, error_msg=None):
    def _category_validator(_, field):
        category = CategoryModel.get(**{db_field: field.data})
        if category is None and must_exist:
            raise ValidationError(error_msg or f'Category with such {db_field} not exists.')
        if category is not None and not must_exist:
            raise ValidationError(error_msg or f'Category with such {db_field} already exists.')
    return _category_validator


def order_validator(db_field, must_exist=True, error_msg=None):
    def _order_validator(_, field):
        product = OrderModel.get(**{db_field: field.data})
        if product is None and must_exist:
            raise ValidationError(error_msg or f'Order with such {db_field} not exists.')
        if product is not None and not must_exist:
            raise ValidationError(error_msg or f'Order with such {db_field} already exists.')
    return _order_validator
