"""Module with carts blueprint and its routes"""

from flask import redirect, render_template, url_for
from flask_login import login_required

from shop.carts.forms import ClearCartForm, PlaceOrderForm, UpdateProductAmountForm
from shop.carts.session_handler import SessionCart


@login_required
def cart():
    update_amount_form = UpdateProductAmountForm(prefix='update_amount')
    clear_cart_form = ClearCartForm(prefix='clear_cart')
    place_order_form = PlaceOrderForm(prefix='place_order')

    if clear_cart_form.validate_on_submit():
        SessionCart.clear_cart()

    if place_order_form.validate_on_submit():
        SessionCart.make_order()

    if update_amount_form.validate_on_submit():
        product_id = update_amount_form.product_id.data
        new_amount = update_amount_form.new_amount.data
        SessionCart.update_product_amount(product_id, new_amount)
        return redirect(url_for('carts_blueprint.cart'))

    context = {
        'items': SessionCart.get_items(),
        'update_amount_form': update_amount_form,
        'clear_cart_form': clear_cart_form,
        'place_order_form': place_order_form,
    }
    return render_template('carts/cart.html', **context)
