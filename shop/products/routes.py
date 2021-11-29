"""Module with users blueprint and its routes"""

from flask import abort, Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from shop.products import forms
from shop.products.helpers import save_product_picture
from shop.products.models import BrandModel, CategoryModel, ProductModel
from shop.users.helpers import admin_required

products_blueprint = Blueprint('products_blueprint', __name__)


@products_blueprint.route("/", methods=['GET', 'POST'])
@products_blueprint.route("/products", methods=['GET', 'POST'])
def products():
    brand_name = request.args.get('brand_name')
    category_name = request.args.get('category_name')

    delete_product_form = forms.DeleteProductForm()
    delete_category_form = forms.DeleteCategoryForm()
    delete_brand_form = forms.DeleteBrandForm()

    if delete_product_form.validate_on_submit():
        if current_user.is_authenticated and current_user.is_superuser:
            product_id = delete_product_form.product_id.data
            product = ProductModel.get(id=product_id)
            product.delete()
        else:
            return abort(403)

    if delete_category_form.validate_on_submit():
        category_id = delete_category_form.category_id.data
        category = CategoryModel.get(id=category_id)
        category.delete()
        return redirect(url_for('products_blueprint.products'))

    if delete_brand_form.validate_on_submit():
        brand_id = delete_brand_form.brand_id.data
        brand = BrandModel.get(id=brand_id)
        brand.delete()
        return redirect(url_for('products_blueprint.products'))

    page = request.args.get('page', 1, type=int)
    paginator = ProductModel.filter(
        category=CategoryModel.get(name=category_name),
        brand=BrandModel.get(name=brand_name),
    ).order_by(ProductModel.name).paginate(page, 8, False)

    context = {
        'pagination': paginator,
        'products': paginator.items,
        'categories': CategoryModel.get_all(),
        'brands': BrandModel.get_all(),
        'delete_product_form': delete_product_form,
        'delete_category_form': delete_category_form,
        'delete_brand_form': delete_brand_form,
        'page': page,
    }
    kwargs = {
        'brand_name': request.args.get('brand_name'),
        'category_name': request.args.get('category_name'),
    }
    print(dict(**request.args))
    return render_template('products/products_list.html', **context, kwargs=kwargs)


@products_blueprint.route("/product_detail/<int:product_id>", methods=['GET', 'POST'])
def product_detail(product_id: int):
    product = ProductModel.get(id=product_id)
    add_to_cart_form = forms.AddToCardForm()
    delete_product_form = forms.DeleteProductForm()

    if product is None:
        return abort(404)

    if add_to_cart_form.validate_on_submit():
        pass

    if delete_product_form.validate_on_submit():
        if current_user.is_authenticated and current_user.is_superuser:
            product_id = delete_product_form.product_id.data
            product = ProductModel.get(id=product_id)
            product.delete()
            return redirect(url_for('products_blueprint.products'))
        return abort(403)

    context = {
        'product': product,
        'add_to_cart_form': add_to_cart_form,
        'delete_product_form': delete_product_form,
    }

    return render_template('products/product_detail.html', **context)


@products_blueprint.route("/create_brand", methods=['GET', 'POST'])
@admin_required
def create_brand():
    form = forms.BrandCreateForm()

    if form.validate_on_submit():
        BrandModel.create(name=form.brand_name.data)
        return redirect(url_for('products_blueprint.products'))

    return render_template('products/create_brand.html', form=form)


@products_blueprint.route("/create_category", methods=['GET', 'POST'])
@admin_required
def create_category():
    form = forms.CategoryCreateForm()

    if form.validate_on_submit():
        CategoryModel.create(name=form.category_name.data)
        return redirect(url_for('products_blueprint.products'))

    return render_template('products/create_category.html', form=form)


@products_blueprint.route("/create_product", methods=['GET', 'POST'])
@admin_required
def create_product():
    form = forms.ProductCreateForm()

    if form.validate_on_submit():
        product = ProductModel.create(
            name=form.name.data,
            short_description=form.short_description.data,
            full_description=form.full_description.data,
            price=form.price.data,
            amount=form.amount.data,
            discount=form.discount.data,
        )
        product.brand = BrandModel.get(name=form.brand.data)
        product.category = CategoryModel.get(name=form.category.data)

        if form.picture.data:
            filename = save_product_picture(form.picture.data)
            product.image_file = filename

        product.save()
        return redirect(url_for('products_blueprint.product_detail', product_id=product.id))

    return render_template('products/create_product.html', form=form)


@products_blueprint.route("/product_update/<int:product_id>", methods=['GET', 'POST'])
@admin_required
def product_update(product_id: int):
    product = ProductModel.get(id=product_id)
    form = forms.ProductUpdateForm()

    if product is None:
        return abort(404)

    if form.validate_on_submit():
        ProductModel.update(
            _id=product.id,
            name=form.name.data,
            short_description=form.short_description.data,
            full_description=form.full_description.data,
            price=form.price.data,
            amount=form.amount.data,
            discount=form.discount.data,
            category_id=CategoryModel.get(name=form.category.data).id,
            brand_id=BrandModel.get(name=form.brand.data).id,
        )
        if form.picture.data:
            filename = save_product_picture(form.picture.data)
            product.update_image_file(filename)

        return redirect(url_for('products_blueprint.product_detail', product_id=product_id))

    if request.method == 'GET':
        initial_data = product.as_dict()
        initial_data['category'] = product.category.name
        initial_data['brand'] = product.brand.name

        form = forms.ProductUpdateForm(**initial_data)

    return render_template('products/update_product.html', form=form)


@products_blueprint.route("/brand_update/<int:brand_id>", methods=['GET', 'POST'])
@admin_required
def brand_update(brand_id: int):
    brand = BrandModel.get(id=brand_id)
    form = forms.BrandUpdateForm()

    if brand is None:
        return abort(404)

    if form.validate_on_submit():
        BrandModel.update(
            _id=brand.id,
            name=form.brand_name.data,
        )
        return redirect(url_for('products_blueprint.products'))

    if request.method == 'GET':
        form = forms.BrandUpdateForm(brand_id=brand_id, brand_name=brand.name)

    return render_template('products/update_brand.html', form=form)


@products_blueprint.route("/category_update/<int:category_id>", methods=['GET', 'POST'])
@admin_required
def category_update(category_id: int):
    category = CategoryModel.get(id=category_id)
    form = forms.CategoryUpdateForm()

    if category is None:
        return abort(404)

    if form.validate_on_submit():
        CategoryModel.update(
            _id=category.id,
            name=form.category_name.data,
        )
        return redirect(url_for('products_blueprint.products'))

    if request.method == 'GET':
        form = forms.CategoryUpdateForm(category_id=category_id, category_name=category.name)

    return render_template('products/update_category.html', form=form)
