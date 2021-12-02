"""Module with forms for orders blueprint"""

from flask_wtf import FlaskForm
from wtforms.fields import IntegerField, SubmitField
from wtforms.validators import DataRequired

from shop.core.validators import order_validator


class MakeCompletedForm(FlaskForm):
    """From for completing order"""

    order_id = IntegerField(
        validators=[DataRequired(), order_validator(db_field='id')],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Done')
