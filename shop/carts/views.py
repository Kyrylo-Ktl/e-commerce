"""Module with carts blueprint and its routes"""

from flask import redirect, render_template, url_for

from shop.carts.forms import UpdateProductAmountForm
from shop.carts.session_handler import SessionCart


def cart():
    update_amount_form = UpdateProductAmountForm()

    if update_amount_form.validate_on_submit():
        product_id = update_amount_form.product_id.data
        new_amount = update_amount_form.new_amount.data
        SessionCart.update_product_amount(product_id, new_amount)
        return redirect(url_for('carts_blueprint.cart'))

    context = {
        'items': SessionCart.get_items(),
        'update_amount_form': update_amount_form,
    }
    return render_template('carts/cart.html', **context)
