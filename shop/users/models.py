"""Models for users blueprint"""
import os

from flask import current_app, render_template, url_for
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from shop.bcrypt import bcrypt
from shop.core.models import BaseModelMixin
from shop.db import db
from shop.email import send_mail


class UserModel(UserMixin, BaseModelMixin):
    __tablename__ = 'users'

    IMAGE_DIR = 'users'
    IMAGE_SIZE = (250, 250)
    DEFAULT_IMAGE = os.path.join(
        'default',
        'default_profile_img.png',
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    _password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    is_superuser = db.Column(db.Boolean, default=False)
    image_file = db.Column(db.String(64), nullable=False, default=DEFAULT_IMAGE)

    __table_args__ = (
        db.CheckConstraint("LENGTH(username) >= 2", name='username_len_constraint'),
        db.CheckConstraint("email LIKE '%@%'", name='email_constraint'),
    )

    def __str__(self):
        return f"<User: ('{self.email}', '{self.username}')>"

    def __repr__(self):
        return f"<User: ('{self.email}', '{self.username}')>"

    def __init__(self, username: str, email: str, password: str,
                 confirmed: bool = False, is_superuser: bool = False, image_file: str = None) -> None:
        self.email = email
        self.username = username
        self.password = password
        self.is_superuser = is_superuser
        self.confirmed = confirmed
        if image_file:
            self.image_file = image_file
        self.save()

    @property
    def password(self) -> str:
        return self._password_hash

    @password.setter
    def password(self, password: str) -> None:
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self._password_hash, password)

    @staticmethod
    def _generate_token(expires_sec: int = 1800, **token_data):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        token = s.dumps(token_data).decode('utf-8')
        return token

    def generate_email_confirmation_token(self, email: str):
        token = UserModel._generate_token(
            user_id=self.id,
            email=email,
        )
        return token

    @staticmethod
    def verify_email_confirmation_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            token_data = s.loads(token)
            UserModel.update(
                _id=token_data['user_id'],
                email=token_data['email'],
                confirmed=True,
            )
        except Exception:
            return False
        return True

    def generate_password_reset_token(self):
        token = UserModel._generate_token(user_id=self.id)
        return token

    @staticmethod
    def verify_password_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return UserModel.get(id=user_id)

    def send_email_confirmation_mail(self, email: str = None):
        token = self.generate_email_confirmation_token(email or self.email)
        confirm_url = url_for('users_blueprint.confirm_email', token=token, _external=True)
        html = render_template('email/confirm.html', confirm_url=confirm_url)

        send_mail(send_to=[email or self.email], subject='Confirm your email', html=html)

    def send_password_reset_mail(self):
        token = self.generate_password_reset_token()
        password_reset_url = url_for('users_blueprint.reset_password', token=token, _external=True)
        html = render_template('email/password_reset.html', password_reset_url=password_reset_url)

        send_mail(send_to=[self.email], subject='Reset password', html=html)

    def update_image_file(self, new_image_file: str):
        if self.image_file != new_image_file:
            self._delete_image_file()
            self.image_file = new_image_file
            self.save()

    def _delete_image_file(self):
        if self.image_file != UserModel.DEFAULT_IMAGE:
            image_path = os.path.join(
                current_app.root_path,
                'static',
                self.image_file,
            )
            os.remove(image_path)

    def delete(self):
        self._delete_image_file()
        return super(UserModel, self).delete()
