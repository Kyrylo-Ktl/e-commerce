"""Module with forms for carts blueprint"""

from flask_wtf import FlaskForm
from wtforms.fields import IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange

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
