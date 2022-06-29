"""Module with users blueprint and its routes"""

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from shop.carts.session_handler import SessionCart
from shop.core.utils import save_picture, verify_token
from shop.orders.models import OrderModel
from shop.users.forms import (
    LoginForm,
    RequestResetPasswordForm,
    ResetPasswordForm,
    SignUpForm,
    UpdatePasswordForm,
    UpdateProfileForm,
)
from shop.users.models import UserModel


def signup():
    if current_user.is_authenticated:
        return redirect(url_for('products_blueprint.products'))

    form = SignUpForm()
    if form.validate_on_submit():
        user = UserModel(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )
        user.send_email_confirmation_mail()

        flash('Your account has been created! You are now need to confirm email', 'success')
        return redirect(url_for('products_blueprint.products'))

    return render_template('users/signup.html', form=form)


def confirm_email(token):
    token_data = verify_token(token)

    if token_data is None:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return abort(404)

    UserModel.update(
        _id=token_data['user_id'],
        email=token_data['email'],
        confirmed=True,
    )
    flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('users_blueprint.login'))


def reset_password(token):
    form = ResetPasswordForm()
    token_data = verify_token(token)

    if token_data is None:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('users_blueprint.reset_password_request'))

    if form.validate_on_submit():
        user = UserModel.get(id=token_data['user_id'])
        user.password = form.password.data
        user.save()
        flash('Password successfully updated', 'success')
        return redirect(url_for('users_blueprint.login'))

    return render_template('users/reset_password.html', form=form)


def login():
    if current_user.is_authenticated:
        return redirect(url_for('products_blueprint.products'))

    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.get(email=form.email.data)

        if user is not None and not user.confirmed:
            flash('Login Unsuccessful. Please confirm your email before first login', 'warning')
        elif user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            SessionCart.init_cart()
            flash('Successfully logged in', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('products_blueprint.products'))
        else:
            flash('Login Unsuccessful. Please check provided email and password', 'danger')

    return render_template('users/login.html', form=form)


@login_required
def profile():
    form = UpdateProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.save()

        if current_user.email != form.email.data:
            current_user.send_email_confirmation_mail(form.email.data)

        if form.picture.data:
            filename = save_picture(form.picture.data, model=UserModel)
            current_user.update_image_file(filename)

    elif request.method == 'GET':
        form = UpdateProfileForm(
            username=current_user.username,
            email=current_user.email,
        )

    page = request.args.get('page', 1, type=int)
    filtered_orders = OrderModel.filter(
        user=current_user,
    ).order_by(OrderModel.created_at.desc())
    paginator = OrderModel.get_pagination(page, filtered_orders, paginate_by=12)

    context = {
        'orders': paginator.items,
        'pagination': paginator,
        'form': form,
        'page': page,
    }

    return render_template('users/profile.html', **context, kwargs={})


@login_required
def update_password():
    form = UpdatePasswordForm()

    if form.validate_on_submit():
        current_user.password = form.new_password.data
        current_user.save()
        return redirect(url_for('users_blueprint.profile'))

    return render_template('users/update_password.html', form=form)


def reset_password_request():
    form = RequestResetPasswordForm()

    if form.validate_on_submit():
        user = UserModel.get(email=form.email.data)
        user.send_password_reset_mail()
        flash('An email with a reset link has been sent to your email', 'success')

    return render_template('users/reset_password_request.html', form=form)


@login_required
def logout():
    logout_user()
    SessionCart.clear_cart()
    flash('You are logged out', 'warning')
    return redirect(url_for('products_blueprint.products'))
