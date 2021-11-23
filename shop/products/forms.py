"""Module with forms for products blueprint"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.fields import FloatField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, ValidationError

from shop.products.models import BrandModel, CategoryModel, ProductModel


class BrandCreateForm(FlaskForm):
    """Form for creating new brand"""

    brand_name = StringField(
        'Brand name',
        validators=[DataRequired('Enter brand name'), Length(min=2, max=64)],
    )
    submit = SubmitField('Create')

    def validate_brand_name(_, field) -> None:
        brand = BrandModel.get(name=field.data)
        if brand is not None:
            raise ValidationError('A brand with this name already exists.')


class BrandUpdateForm(BrandCreateForm):
    """Form for updating brand data"""

    brand_id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Update')

    def validate_brand_name(_, field) -> None:
        pass

    def validate(self, extra_validators=None):
        if not super(BrandCreateForm, self).validate(extra_validators):
            return False

        brand = BrandModel.get(name=self.brand_name.data)
        if brand is not None and brand.id != self.brand_id.data:
            self.brand_name.errors.append('Brand with such title already exists.')
            return False

        return True


class CategoryCreateForm(FlaskForm):
    """Form for creating new category"""

    category_name = StringField(
        'Category name',
        validators=[DataRequired('Enter category name'), Length(min=2, max=64)],
    )
    submit = SubmitField('Create')

    def validate_category_name(_, field) -> None:
        category = CategoryModel.get(name=field.data)
        if category is not None:
            raise ValidationError('A category with this name already exists.')


class CategoryUpdateForm(CategoryCreateForm):
    """Form for updating category"""

    category_id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Update')

    def validate_category_name(_, field) -> None:
        pass

    def validate(self, extra_validators=None):
        if not super(CategoryCreateForm, self).validate(extra_validators):
            return False

        category = CategoryModel.get(name=self.category_name.data)
        if category is not None and category.id != self.category_id.data:
            self.category_name.errors.append('Category with such title already exists.')
            return False

        return True


class ProductCreateForm(FlaskForm):
    """Form for creating new product"""

    name = StringField(
        'Product name',
        validators=[DataRequired('Enter product name'), Length(min=2, max=64)],
    )
    short_description = TextAreaField(
        'Short description',
        validators=[DataRequired('Enter short description'), Length(min=16, max=256)],
        render_kw={'rows': 5},
    )
    full_description = TextAreaField(
        'Full description',
        validators=[DataRequired('Enter full description'), Length(min=64, max=1028)],
        render_kw={'rows': 10},
    )
    price = FloatField(
        'Price',
        validators=[DataRequired('Enter positive price'), NumberRange(min=0.01, max=1_000_000)],
    )
    amount = IntegerField(
        'Available amount',
        validators=[InputRequired("You must enter some amount!"), NumberRange(min=0, max=1_000_000)],
    )
    discount = IntegerField(
        'Discount percent',
        validators=[InputRequired("You must enter some percent!"), NumberRange(min=0, max=99)],
    )

    brand = SelectField(validators=[DataRequired()])
    category = SelectField(validators=[DataRequired()])

    picture = FileField(
        'Load product image',
        validators=[FileAllowed(['jpg', 'png'])],
    )
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        self.category.choices = CategoryModel.get_all()
        self.brand.choices = BrandModel.get_all()

    def validate_name(_, field) -> None:
        product = ProductModel.get(name=field.data)
        if product is not None:
            raise ValidationError('A product with this name already exists.')


class ProductUpdateForm(ProductCreateForm):
    """Form for updating product"""

    id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Update')

    def validate_name(_, field) -> None:
        pass

    def validate(self, extra_validators=None):
        if not super(ProductUpdateForm, self).validate(extra_validators):
            return False

        product = ProductModel.get(name=self.name.data)
        if product is not None and product.id != self.id.data:
            self.name.errors.append('Product with such title already exists.')
            return False

        return True


class AddToCardForm(FlaskForm):
    """Form for adding a product to the cart"""

    product_id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    amount_to_add = IntegerField(
        'Enter amount to add:',
        default=1,
        validators=[DataRequired('Enter positive amount'), NumberRange(min=1, max=100)],
    )
    submit = SubmitField('Add to cart')

    def validate_product_id(_, field) -> None:
        product = ProductModel.get(id=field.data)
        if product is None:
            raise ValidationError('Product with such id not exists.')

    def validate(self, extra_validators=None) -> bool:
        if not FlaskForm.validate(self, extra_validators=None):
            return False

        product = ProductModel.get(id=self.product_id.data)
        if product.amount < self.amount_to_add.data:
            self.amount_to_add.errors.append('Not enough product to add.')
            return False

        return True


class DeleteProductForm(FlaskForm):
    """Product removal form"""

    product_id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Delete')


class DeleteCategoryForm(FlaskForm):
    """Category removal form"""

    category_id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Delete')


class DeleteBrandForm(FlaskForm):
    """Brand removal form"""

    brand_id = IntegerField(
        validators=[DataRequired()],
        render_kw={'hidden': True},
    )
    submit = SubmitField('Delete')
