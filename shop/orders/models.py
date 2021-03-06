"""Models for orders blueprint"""

from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import backref

from shop.core.models import BaseModelMixin
from shop.db import db
from shop.products.models import ProductModel


class OrderProductModel(BaseModelMixin):
    """Many-to-Many relationship model between Order and Product"""
    __tablename__ = 'order_product'

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )
    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )
    amount = db.Column(db.Integer, default=1)

    product = db.relationship(
        'ProductModel',
        primaryjoin=product_id == ProductModel.id,
    )

    __table_args__ = (
        CheckConstraint('0 < amount'),
    )


class OrderModel(BaseModelMixin):
    """Entity Order Model"""

    __tablename__ = 'orders'

    PAGINATE_BY = 20

    id = db.Column(db.Integer, primary_key=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', backref=backref('orders', cascade='all,delete'))

    products = db.relationship(
        'OrderProductModel',
        lazy='dynamic',
        cascade='all, delete',
        backref='order',
    )

    def __str__(self) -> str:
        return f"<Order: (user={self.user.email}, completed={self.is_completed})>"

    def __repr__(self) -> str:
        return f"<Order: (user={self.user.email}, completed={self.is_completed})>"

    @property
    def total_items(self):
        items = sum(order_product.amount for order_product in self.products.all())
        return items

    @property
    def total_sum(self):
        items_sum = sum(ord_pr.amount * ord_pr.product.discount_price for ord_pr in self.products.all())
        items_sum = round(items_sum, 2)
        return items_sum

    def add_product(self, product: ProductModel, amount: int = 1) -> OrderProductModel:
        return OrderProductModel.create(
            order=self,
            product=product,
            amount=amount,
        )

    def complete(self):
        for order_product in self.products.all():
            order_product.product.amount -= order_product.amount
            order_product.product.reserved -= order_product.amount
        self.is_completed = True
        self.save()
