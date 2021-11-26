"""Module with forms for users blueprint"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from shop.users.models import UserModel


class SignUpForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=2, max=16),
        ],
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
        ],
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password'),
        ],
    )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = UserModel.get(username=username.data)
        if user is not None:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = UserModel.get(email=email.data)
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
        ],
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
