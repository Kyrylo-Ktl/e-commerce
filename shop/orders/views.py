"""Module with orders blueprint and its routes"""

from flask import render_template, request

from shop.orders.models import OrderModel
from shop.users.helpers import admin_required
from shop.orders.forms import MakeCompletedForm


@admin_required
def orders_list():
    mark_complete_form = MakeCompletedForm()

    if mark_complete_form.validate_on_submit():
        order_id = mark_complete_form.order_id.data
        order = OrderModel.get(id=order_id)

        if not order.is_completed:
            order.complete()

    is_completed = request.args.get('completed')
    page = request.args.get('page', 1, type=int)
    filtered_orders = OrderModel.filter(
        is_completed=is_completed,
    ).order_by(OrderModel.created_at.desc())
    paginator = OrderModel.get_pagination(page, filtered_orders)

    context = {
        'orders': paginator.items,
        'pagination': paginator,
        'form': mark_complete_form,
        'page': page,
    }
    kwargs = {
        'completed': is_completed,
    }
    return render_template('orders/orders_list.html', **context, kwargs=kwargs)
