"""Module with users blueprint and its routes"""

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, logout_user, current_user

from shop.users.forms import RegistrationForm, LoginForm
from shop.users.models import UserModel

users_blueprint = Blueprint('users_blueprint', __name__)


@users_blueprint.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('core_blueprint.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        UserModel(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users_blueprint.login'))

    return render_template('users/signup.html', title='SignUp', form=form)


@users_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core_blueprint.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.get(email=form.email.data)

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            if next_page:
                return redirect(next_page)

            flash('Successfully logged in', 'success')
            return redirect(url_for('core_blueprint.home'))
        else:
            flash('Login Unsuccessful. Please check provided email and password', 'danger')

    return render_template('users/login.html', title='Login', form=form)


@users_blueprint.route("/logout")
def logout():
    logout_user()
    flash('You are logged out', 'info')
    return redirect(url_for('core_blueprint.home'))
