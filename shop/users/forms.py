"""Module with forms for users blueprint"""
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from shop.core.validators import user_validator
from shop.users.models import UserModel


class SignUpForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(), Length(min=2, max=16),
            user_validator(db_field='username', must_exist=False,
                           error_msg='That username is taken. Please choose a different one.'),
        ],
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(), Email(),
            user_validator(db_field='email', must_exist=False,
                           error_msg='That email is taken. Please choose a different one.'),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')],
    )
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
    )
    picture = FileField(
        'Load new profile image',
        validators=[FileAllowed(['jpg', 'png'])],
    )
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username and UserModel.get(username=username.data):
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email and UserModel.get(email=email.data):
            raise ValidationError('That email is taken. Please choose a different one.')


class UpdatePasswordForm(FlaskForm):
    password = PasswordField(
        'Current password',
        validators=[DataRequired()],
    )
    new_password = PasswordField(
        'New password',
        validators=[DataRequired()],
    )
    confirm_new_password = PasswordField(
        'Confirm new password',
        validators=[DataRequired(), EqualTo('new_password')],
    )
    submit = SubmitField('Update')

    def validate_password(self, password):
        if not current_user.check_password(password.data):
            raise ValidationError('Invalid password')


class RequestResetPasswordForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(), Email(),
            user_validator('email', must_exist=True,
                           error_msg='There is no account with that email. You must register first.'),
        ],
    )
    submit = SubmitField('Send password reset request')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password')],
    )
    submit = SubmitField('Set password')
