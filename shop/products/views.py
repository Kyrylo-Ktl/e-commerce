"""Module with users blueprint and its routes"""

from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user

from shop.carts import forms as cart_forms
from shop.carts.session_handler import SessionCart
from shop.core.utils import save_picture
from shop.products import forms as product_forms
from shop.products.models import BrandModel, CategoryModel, ProductModel
from shop.users.helpers import admin_required


def products():
    brand_name = request.args.get('brand_name')
    category_name = request.args.get('category_name')

    delete_product_form = product_forms.DeleteProductForm(prefix='delete_product')
    delete_category_form = product_forms.DeleteCategoryForm(prefix='delete_category')
    delete_brand_form = product_forms.DeleteBrandForm(prefix='delete_brand')
    add_to_cart_form = product_forms.AddOneToCardForm(prefix='add_to_cart')

    if delete_product_form.validate_on_submit():
        if current_user.is_authenticated and current_user.is_superuser:
            product_id = delete_product_form.product_id.data
            product = ProductModel.get(id=product_id)
            product.delete()
        else:
            return abort(403)

    if add_to_cart_form.validate_on_submit():
        if current_user.is_authenticated:
            product_id = add_to_cart_form.product_id.data
            SessionCart.add_product(product_id, 1)
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
    filtered_products = ProductModel.filter(
        category=CategoryModel.get(name=category_name),
        brand=BrandModel.get(name=brand_name),
    ).order_by(ProductModel.name)
    paginator = ProductModel.get_pagination(page, filtered_products)

    context = {
        'products': paginator.items,
        'pagination': paginator,
        'page': page,
        'categories': CategoryModel.get_all(),
        'brands': BrandModel.get_all(),
        'delete_product_form': delete_product_form,
        'delete_category_form': delete_category_form,
        'delete_brand_form': delete_brand_form,
        'add_to_cart_form': add_to_cart_form,
    }

    kwargs = {
        'brand_name': request.args.get('brand_name'),
        'category_name': request.args.get('category_name'),
    }
    return render_template('products/products_list.html', **context, kwargs=kwargs)


def product_detail(product_id: int):
    product = ProductModel.get(id=product_id)
    add_to_cart_form = cart_forms.AddToCardForm(prefix='add_to_card')
    delete_product_form = product_forms.DeleteProductForm(prefix='delete_product')

    if product is None:
        return abort(404)

    if add_to_cart_form.validate_on_submit():
        product_id = add_to_cart_form.product_id.data
        amount = add_to_cart_form.amount_to_add.data
        SessionCart.add_product(product_id, amount)

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


@admin_required
def create_brand():
    form = product_forms.BrandCreateForm()

    if form.validate_on_submit():
        BrandModel.create(name=form.brand_name.data)
        return redirect(url_for('products_blueprint.products'))

    return render_template('products/create_brand.html', form=form)


@admin_required
def create_category():
    form = product_forms.CategoryCreateForm()

    if form.validate_on_submit():
        CategoryModel.create(name=form.category_name.data)
        return redirect(url_for('products_blueprint.products'))

    return render_template('products/create_category.html', form=form)


@admin_required
def create_product():
    form = product_forms.ProductCreateForm()

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
            filename = save_picture(form.picture.data, model=ProductModel)
            product.image_file = filename

        product.save()
        return redirect(url_for('products_blueprint.product_detail', product_id=product.id))

    return render_template('products/create_product.html', form=form)


@admin_required
def product_update(product_id: int):
    product = ProductModel.get(id=product_id)
    form = product_forms.ProductUpdateForm()

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
            filename = save_picture(form.picture.data, model=ProductModel)
            product.update_image_file(filename)

        return redirect(url_for('products_blueprint.product_detail', product_id=product_id))

    if request.method == 'GET':
        initial_data = product.as_dict()
        initial_data['category'] = product.category.name
        initial_data['brand'] = product.brand.name

        form = product_forms.ProductUpdateForm(**initial_data)

    return render_template('products/update_product.html', form=form)


@admin_required
def brand_update(brand_id: int):
    brand = BrandModel.get(id=brand_id)
    form = product_forms.BrandUpdateForm()

    if brand is None:
        return abort(404)

    if form.validate_on_submit():
        BrandModel.update(
            _id=brand.id,
            name=form.brand_name.data,
        )
        return redirect(url_for('products_blueprint.products'))

    if request.method == 'GET':
        form = product_forms.BrandUpdateForm(brand_id=brand_id, brand_name=brand.name)

    return render_template('products/update_brand.html', form=form)


@admin_required
def category_update(category_id: int):
    category = CategoryModel.get(id=category_id)
    form = product_forms.CategoryUpdateForm()

    if category is None:
        return abort(404)

    if form.validate_on_submit():
        CategoryModel.update(
            _id=category.id,
            name=form.category_name.data,
        )
        return redirect(url_for('products_blueprint.products'))

    if request.method == 'GET':
        form = product_forms.CategoryUpdateForm(category_id=category_id, category_name=category.name)

    return render_template('products/update_category.html', form=form)
