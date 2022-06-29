"""Module with carts blueprint and its routes"""

from flask import abort, render_template
from flask_login import current_user, login_required

from shop.carts.forms import ClearCartForm, PlaceOrderForm, UpdateProductAmountForm
from shop.carts.session_handler import SessionCart


@login_required
def cart():
    update_amount_form = UpdateProductAmountForm(prefix='update_amount')
    clear_cart_form = ClearCartForm(prefix='clear_cart')
    place_order_form = PlaceOrderForm(prefix='place_order')

    if current_user.is_superuser:
        return abort(403)

    if clear_cart_form.validate_on_submit() and clear_cart_form.submit.data:
        SessionCart.clear_cart()

    if place_order_form.validate_on_submit() and place_order_form.submit.data:
        if not SessionCart.is_empty():
            SessionCart.make_order()
        else:
            return abort(409)

    if update_amount_form.validate_on_submit():
        product_id = update_amount_form.product_id.data
        new_amount = update_amount_form.new_amount.data
        SessionCart.update_product_amount(product_id, new_amount)

    context = {
        'items': SessionCart.get_items(),
        'update_amount_form': update_amount_form,
        'clear_cart_form': clear_cart_form,
        'place_order_form': place_order_form,
    }
    return render_template('carts/cart.html', **context)
