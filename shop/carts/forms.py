"""Module with forms for carts blueprint"""

from flask import session
from flask_wtf import FlaskForm
from wtforms.fields import IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange

from shop.carts.session_handler import SessionCart
from shop.core.validators import product_validator
from shop.products.models import ProductModel


class AddToCardForm(FlaskForm):
    """Form for adding a product to the cart"""

    product_id = IntegerField(
        validators=[DataRequired(), product_validator(db_field='id')],
        render_kw={'hidden': True},
    )
    amount_to_add = IntegerField(
        'Enter amount to add:',
        default=1,
        validators=[DataRequired('Enter positive amount'), NumberRange(min=1, max=100)],
    )
    submit = SubmitField('Add to cart')

    def validate(self, extra_validators=None) -> bool:
        if not FlaskForm.validate(self, extra_validators=None):
            return False

        product = ProductModel.get(id=self.product_id.data)
        if product.available < self.amount_to_add.data:
            self.amount_to_add.errors.append('Not enough product to add.')
            return False
        return True


class UpdateProductAmountForm(FlaskForm):
    """Product amount updating form"""

    product_id = IntegerField(
        validators=[DataRequired(), product_validator(db_field='id')],
        render_kw={'hidden': True},
    )
    new_amount = IntegerField(
        validators=[InputRequired(), NumberRange(min=0)],
    )

    def validate(self, extra_validators=None) -> bool:
        if not FlaskForm.validate(self, extra_validators=None):
            return False

        product = ProductModel.get(id=self.product_id.data)
        max_amount = product.available + session[SessionCart.CART_NAME].get(str(product.id), 0)
        if max_amount < self.new_amount.data:
            self.new_amount.errors.append('Not enough product to add.')
            return False
        return True


class ClearCartForm(FlaskForm):
    submit = SubmitField('Clear cart')


class PlaceOrderForm(FlaskForm):
    submit = SubmitField('Place order')
