"""Models for users blueprint"""

from flask_login import UserMixin

from shop.core.models import BaseModelMixin
from shop.db import db
from shop.bcrypt import bcrypt


class UserModel(UserMixin, BaseModelMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    _password_hash = db.Column(db.String(128))
    is_superuser = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.CheckConstraint("LENGTH(username) >= 2", name='username_len_constraint'),
        db.CheckConstraint("email LIKE '%@%'", name='email_constraint'),
    )

    def __init__(self, username: str, email: str, password: str) -> None:
        self.email = email
        self.username = username
        self.password = password
        self.save()

    def __str__(self):
        return f"<User: ('{self.email}', '{self.username}')>"

    @property
    def password(self) -> str:
        return self._password_hash

    @password.setter
    def password(self, password: str) -> None:
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self._password_hash, password)
