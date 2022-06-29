import secrets
import unittest

from tests.utils import login, logout

from shop import create_app
from shop.db import db
from shop.seed_db import fake
from shop.users.models import UserModel


class BaseTestMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.app_context().push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.reflect()
        db.drop_all()


class ClientRequestsMixin(BaseTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ctx = cls.app.test_request_context()
        cls._ctx.push()

        cls.client = cls.app.test_client()


class SuperuserMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_username = fake.name()
        cls.admin_password = secrets.token_hex(16)
        cls.admin_email = fake.email()

        cls.admin = UserModel.create(
            email=cls.admin_email,
            username=cls.admin_username,
            password=cls.admin_password,
            confirmed=True,
            is_superuser=True,
        )

    def setUp(self):
        login(self.client, self.admin_email, self.admin_password)

    def tearDown(self):
        logout(self.client)
        super().tearDown()


class UserMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_username = fake.name()
        cls.user_password = secrets.token_hex(16)
        cls.user_email = fake.email()

        cls.user = UserModel.create(
            email=cls.user_email,
            username=cls.user_username,
            password=cls.user_password,
            confirmed=True,
        )

    def setUp(self):
        login(self.client, self.user_email, self.user_password)

    def tearDown(self):
        logout(self.client)
        super().tearDown()
