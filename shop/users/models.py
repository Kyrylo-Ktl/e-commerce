"""Models for users blueprint"""

import os

from flask_login import UserMixin

from shop.bcrypt import bcrypt
from shop.core.models import BaseModelMixin, PictureHandleMixin
from shop.core.utils import generate_token
from shop.db import db
from shop.email import send_token_url_mail


class UserModel(UserMixin, PictureHandleMixin, BaseModelMixin):
    __tablename__ = 'users'

    IMAGE_DIR = __tablename__
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

    def generate_email_confirmation_token(self, email: str):
        token = generate_token(user_id=self.id, email=email)
        return token

    def generate_password_reset_token(self):
        token = generate_token(user_id=self.id)
        return token

    def send_email_confirmation_mail(self, email: str = None):
        send_token_url_mail(
            email=email or self.email,
            subject='Confirm your email',
            token=self.generate_email_confirmation_token(email or self.email),
            url='users_blueprint.confirm_email',
            template='confirm',
        )

    def send_password_reset_mail(self):
        send_token_url_mail(
            email=self.email,
            subject='Reset password',
            token=self.generate_password_reset_token(),
            url='users_blueprint.reset_password',
            template='password_reset',
        )
