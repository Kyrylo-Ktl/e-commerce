"""Models for users blueprint"""

import os
from typing import List, Optional

from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import BaseQuery, Pagination
from sqlalchemy.orm import backref

from shop.core.models import BaseModelMixin
from shop.db import db


class BrandModel(UserMixin, BaseModelMixin):
    """Entity Brand Model"""

    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    __table_args__ = (
        db.CheckConstraint('LENGTH(name) >= 2', name='brand_name_len_constraint'),
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Brand: ('{self.name}')>"

    def delete(self) -> None:
        for product in self.products:
            product.delete()
        return super(BrandModel, self).delete()

    @classmethod
    def get_all(cls) -> List:
        return cls.query.order_by(cls.name).all()


class CategoryModel(UserMixin, BaseModelMixin):
    """Entity Category Model"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    __table_args__ = (
        db.CheckConstraint('LENGTH(name) >= 2', name='category_name_len_constraint'),
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Category: ('{self.name}')>"

    def delete(self) -> None:
        for product in self.products:
            product.delete()
        return super(CategoryModel, self).delete()

    @classmethod
    def get_all(cls) -> List:
        return cls.query.order_by(cls.name).all()


class ProductModel(UserMixin, BaseModelMixin):
    """Entity Product Model"""

    __tablename__ = 'products'

    PAGINATE_BY = 8
    IMAGE_DIR = 'products'
    IMAGE_SIZE = (500, 500)
    DEFAULT_IMAGE = os.path.join(
        'default',
        'default.png',
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    short_description = db.Column(db.String(256))
    full_description = db.Column(db.String(1028))
    price = db.Column(db.Float)
    amount = db.Column(db.Integer)
    reserved = db.Column(db.Integer, default=0)
    discount = db.Column(db.Integer)

    image_file = db.Column(db.String(64), nullable=False, default=DEFAULT_IMAGE)

    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    brand = db.relationship('BrandModel', backref=backref('products', cascade='all,delete'))

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('CategoryModel', backref=backref('products', cascade='all,delete'))

    __table_args__ = (
        db.CheckConstraint('price >= 0.01', name='product_positive_price_constraint'),
        db.CheckConstraint('amount >= 0', name='product_non_negative_amount_constraint'),
        db.CheckConstraint('reserved <= amount', name='product_valid_reserved_amount_constraint'),
        db.CheckConstraint('discount >= 0 AND discount <= 99', name='valid_product_discount_constraint'),
    )

    def __str__(self) -> str:
        return f"<Product: ('{self.name}')>"

    def __repr__(self) -> str:
        return f"<Product: ('{self.name}')>"

    @property
    def discount_price(self):
        return round(self.price * (1 - self.discount / 100), 2)

    @property
    def available(self):
        return self.amount - self.reserved

    def update_image_file(self, new_image_file: str):
        if self.image_file != new_image_file:
            self._delete_image_file()
            self.image_file = new_image_file
            self.save()

    def _delete_image_file(self) -> None:
        if self.image_file != ProductModel.DEFAULT_IMAGE:
            image_path = os.path.join(
                current_app.root_path,
                'static',
                self.image_file,
            )
            os.remove(image_path)

    def delete(self) -> None:
        self._delete_image_file()
        return super(ProductModel, self).delete()
