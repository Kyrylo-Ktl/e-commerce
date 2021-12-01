"""Module with users blueprint and its routes"""

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from itsdangerous import exc

from shop.carts.session_handler import SessionCart
from shop.email import send_mail
from shop.users.forms import LoginForm, SignUpForm
from shop.users.helpers import confirm_token
from shop.users.helpers import generate_confirmation_token
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

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('users_blueprint.confirm_email', token=token, _external=True)
        html = render_template('email/confirm.html', confirm_url=confirm_url)

        send_mail(send_to=[user.email], subject="Confirm your email", html=html)

        flash('Your account has been created! You are now need to confirm email', 'success')
        return redirect(url_for('products_blueprint.products'))

    return render_template('users/signup.html', title='SignUp', form=form)


def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('products_blueprint.products'))

    try:
        email = confirm_token(token)
    except exc.BadSignature:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('products_blueprint.products'))

    user = UserModel.get(email=email)
    if user is None:
        return abort(404)
    elif user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('users_blueprint.login'))
    else:
        user.confirmed = True
        user.save()
        flash('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('users_blueprint.login'))


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
            next_page = request.args.get('next')

            if next_page:
                return redirect(next_page)

            flash('Successfully logged in', 'success')
            return redirect(url_for('products_blueprint.products'))
        else:
            flash('Login Unsuccessful. Please check provided email and password', 'danger')

    return render_template('users/login.html', title='Login', form=form)


@login_required
def logout():
    logout_user()
    SessionCart.clear_cart()
    flash('You are logged out', 'warning')
    return redirect(url_for('products_blueprint.products'))
