import secrets
import unittest

from flask import url_for
from tests.mixins import ClientRequestsMixin, UserMixin
from tests.utils import captured_templates, logout

from shop.email import mail
from shop.orders.models import OrderModel
from shop.seed_db import (
    fake,
    seed_brands,
    seed_categories,
    seed_orders,
    seed_products,
)
from shop.users.models import UserModel

unittest.TestCase.maxDiff = None


class SignupPageTests(ClientRequestsMixin):
    def tearDown(self) -> None:
        UserModel.delete_all()
        super().tearDown()

    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('users_blueprint.signup'))

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/signup.html', template.name)

    def test_post_registration_credentials(self):
        with captured_templates(self.app) as templates, mail.record_messages() as outbox:
            password = secrets.token_hex(16)
            post_data = {
                'email': fake.email(),
                'username': fake.first_name(),
                'password': password,
                'confirm_password': password,
            }
            response = self.client.post(
                url_for('users_blueprint.signup'),
                data=post_data,
            )

            expected_redirect_url = url_for('products_blueprint.products', _external=True)
            self.assertEqual(expected_redirect_url, response.location)
            self.assertEqual(1, len(templates))

            self.assertEqual(1, len(UserModel.get_all()))
            user = UserModel.get(email=post_data['email'])
            self.assertIsNotNone(user)
            self.assertFalse(user.confirmed)
            self.assertFalse(user.is_superuser)

            template, context = templates[0]
            self.assertEqual('email/confirm.html', template.name)

            expected_token = user.generate_email_confirmation_token(post_data['email'])
            expected_url = url_for('users_blueprint.confirm_email', token=expected_token, _external=True)
            self.assertEqual(expected_url, context['token_url'])

            self.assertEqual(1, len(outbox))
            sent_mail = outbox[0]
            self.assertEqual('Confirm your email', sent_mail.subject)
            self.assertEqual([post_data['email']], sent_mail.recipients)
            self.assertTrue(expected_url in sent_mail.html)

    def test_post_registration_with_taken_email(self):
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=secrets.token_hex(16),
        )

        with captured_templates(self.app) as templates, mail.record_messages() as outbox:
            password = secrets.token_hex(16)
            post_data = {
                'email': user.email,
                'username': fake.first_name(),
                'password': password,
                'confirm_password': password,
            }
            response = self.client.post(
                url_for('users_blueprint.signup'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            self.assertEqual(1, len(UserModel.get_all()))
            user = UserModel.get(email=post_data['email'])
            self.assertIsNotNone(user)
            self.assertNotEqual(str(user.username), post_data['username'])

            template, context = templates[0]
            self.assertEqual('users/signup.html', template.name)
            actual_error = str(context['form'].errors['email'][0])
            self.assertEqual('That email is taken. Please choose a different one.', actual_error)

            self.assertEqual(0, len(outbox))

    def test_post_registration_with_taken_username(self):
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=secrets.token_hex(16),
        )

        with captured_templates(self.app) as templates, mail.record_messages() as outbox:
            password = secrets.token_hex(16)
            post_data = {
                'email': fake.email(),
                'username': user.username,
                'password': password,
                'confirm_password': password,
            }
            response = self.client.post(
                url_for('users_blueprint.signup'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            self.assertEqual(1, len(UserModel.get_all()))
            user = UserModel.get(username=post_data['username'])
            self.assertIsNotNone(user)
            self.assertNotEqual(user.email, post_data['email'])

            template, context = templates[0]
            self.assertEqual('users/signup.html', template.name)

            actual_error = str(context['form'].errors['username'][0])
            self.assertEqual('That username is taken. Please choose a different one.', actual_error)

            self.assertEqual(0, len(outbox))


class ConfirmEmailPageTests(ClientRequestsMixin):
    def tearDown(self) -> None:
        UserModel.delete_all()
        super().tearDown()

    def test_get_page_with_invalid_token(self):
        response = self.client.get(url_for(
            'users_blueprint.confirm_email',
            token=secrets.token_hex(32),
        ))

        self.assertEqual(404, response.status_code)
        self.assertEqual(0, len(UserModel.get_all()))

    def test_get_page_with_valid_token(self):
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=secrets.token_hex(16),
        )
        self.assertFalse(user.confirmed)

        response = self.client.get(url_for(
            'users_blueprint.confirm_email',
            token=user.generate_email_confirmation_token(user.email),
        ))

        self.assertEqual(302, response.status_code)
        expected_redirect_url = url_for('users_blueprint.login', _external=True)
        self.assertEqual(expected_redirect_url, response.location)

        user = UserModel.get(email=user.email)
        self.assertIsNotNone(user)
        self.assertTrue(user.confirmed)


class LoginPageTests(ClientRequestsMixin):
    def tearDown(self) -> None:
        logout(self.client)
        UserModel.delete_all()
        super().tearDown()

    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('users_blueprint.login'))

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            self.assertEqual(0, len(UserModel.get_all()))

            template, context = templates[0]
            self.assertEqual('users/login.html', template.name)

    def test_post_login(self):
        password = secrets.token_hex(16)
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=password,
            confirmed=True,
        )

        post_data = {
            'email': user.email,
            'password': password,
        }
        response = self.client.post(
            url_for('users_blueprint.login'),
            data=post_data,
        )

        self.assertEqual(302, response.status_code)
        expected_redirect_url = url_for('products_blueprint.products', _external=True)
        self.assertEqual(expected_redirect_url, response.location)

    def test_post_login_invalid_email(self):
        password = secrets.token_hex(16)
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=password,
            confirmed=True,
        )

        with captured_templates(self.app) as templates:
            post_data = {
                'email': user.email + 'x',
                'password': password,
            }
            response = self.client.post(
                url_for('users_blueprint.login'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/login.html', template.name)

    def test_post_login_invalid_password(self):
        password = secrets.token_hex(16)
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=password,
            confirmed=True,
        )

        with captured_templates(self.app) as templates:
            post_data = {
                'email': user.email,
                'password': password + 'x',
            }
            response = self.client.post(
                url_for('users_blueprint.login'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/login.html', template.name)

    def test_post_login_non_confirmed_email(self):
        password = secrets.token_hex(16)
        user = UserModel(
            email=fake.email(),
            username=fake.first_name(),
            password=password,
        )

        with captured_templates(self.app) as templates:
            post_data = {
                'email': user.email,
                'password': password,
            }
            response = self.client.post(
                url_for('users_blueprint.login'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/login.html', template.name)


class ProfilePageTests(UserMixin, ClientRequestsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        seed_brands(n_brands=5)
        seed_categories(n_categories=5)
        seed_products(n_products=20)

    def tearDown(self):
        super().tearDown()
        OrderModel.delete_all()

    def test_get_page(self):
        seed_orders(n_orders=10)

        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('users_blueprint.profile'))

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/profile.html', template.name)
            expected_orders = set(OrderModel.get_all())
            self.assertSetEqual(expected_orders, set(context['orders']))

    def test_post_change_username(self):
        new_username = self.user.username[::-1]
        post_data = {
            'username': new_username,
            'email':  self.user.email,
            'picture': None,
            'submit': True,
        }
        response = self.client.post(
            url_for('users_blueprint.profile'),
            data=post_data,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user.id, UserModel.get(username=new_username).id)

    def test_post_change_email(self):
        new_email = fake.email()
        post_data = {
            'username': self.user.username,
            'email':  new_email,
            'picture': None,
            'submit': True,
        }

        with captured_templates(self.app) as templates, mail.record_messages() as outbox:
            response = self.client.post(
                url_for('users_blueprint.profile'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertIsNone(UserModel.get(username=new_email))

            self.assertEqual(2, len(templates))
            template, context = templates[0]
            self.assertEqual('email/confirm.html', template.name)

            expected_token = self.user.generate_email_confirmation_token(new_email)
            expected_url = url_for('users_blueprint.confirm_email', token=expected_token, _external=True)
            self.assertEqual(expected_url, context['token_url'])

            self.assertEqual(1, len(outbox))
            sent_mail = outbox[0]
            self.assertEqual('Confirm your email', sent_mail.subject)
            self.assertEqual([new_email], sent_mail.recipients)
            self.assertTrue(expected_url in sent_mail.html)


class UpdatePasswordPageTests(UserMixin, ClientRequestsMixin):
    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('users_blueprint.update_password'))

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/update_password.html', template.name)

    def test_send_post_with_valid_password(self):
        new_password = secrets.token_hex(16)
        post_data = {
            'password': self.user_password,
            'new_password': new_password,
            'confirm_new_password': new_password,
        }
        response = self.client.post(
            url_for('users_blueprint.update_password'),
            data=post_data,
        )

        self.assertEqual(302, response.status_code)
        expected_redirect_url = url_for('users_blueprint.profile', _external=True)
        self.assertEqual(expected_redirect_url, response.location)

        self.assertTrue(self.user.check_password(new_password))

    def test_send_post_with_invalid_password(self):
        new_password = secrets.token_hex(16)
        post_data = {
            'password': secrets.token_hex(16),
            'new_password': new_password,
            'confirm_new_password': new_password,
        }

        with captured_templates(self.app) as templates:
            response = self.client.post(
                url_for('users_blueprint.update_password'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertFalse(self.user.check_password(new_password))

            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('users/update_password.html', template.name)

            actual_error = str(context['form'].errors['password'][0])
            self.assertEqual('Invalid password', actual_error)


class ResetPasswordRequestPageTests(UserMixin, ClientRequestsMixin):
    def test_get_page(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for('users_blueprint.reset_password_request'))

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/reset_password_request.html', template.name)

    def test_post_existing_email(self):
        with captured_templates(self.app) as templates, mail.record_messages() as outbox:
            post_data = {
                'email': self.user.email,
                'submit': True,
            }
            response = self.client.post(
                url_for('users_blueprint.reset_password_request'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(templates))

            template, context = templates[1]
            self.assertEqual('users/reset_password_request.html', template.name)
            self.assertEqual({}, context['form'].errors)

            template, context = templates[0]
            self.assertEqual('email/password_reset.html', template.name)

            expected_token = self.user.generate_password_reset_token()
            expected_url = url_for('users_blueprint.reset_password', token=expected_token, _external=True)
            self.assertEqual(expected_url, context['token_url'])

            self.assertEqual(1, len(outbox))
            sent_mail = outbox[0]
            self.assertEqual('Reset password', sent_mail.subject)
            self.assertEqual([post_data['email']], sent_mail.recipients)
            self.assertTrue(expected_url in sent_mail.html)

    def test_post_non_existing_email(self):
        with captured_templates(self.app) as templates, mail.record_messages() as outbox:
            post_data = {
                'email': fake.email(),
                'submit': True,
            }
            response = self.client.post(
                url_for('users_blueprint.reset_password_request'),
                data=post_data,
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))

            template, context = templates[0]
            self.assertEqual('users/reset_password_request.html', template.name)
            actual_error = str(context['form'].errors['email'][0])
            self.assertEqual('There is no account with that email. You must register first.', actual_error)

            self.assertEqual(0, len(outbox))


class ResetPasswordPageTests(UserMixin, ClientRequestsMixin):
    def test_get_page_with_invalid_token(self):
        response = self.client.get(url_for(
            'users_blueprint.reset_password',
            token=secrets.token_hex(32),
        ))

        self.assertEqual(302, response.status_code)
        expected_redirect_url = url_for('users_blueprint.reset_password_request', _external=True)
        self.assertEqual(expected_redirect_url, response.location)

    def test_get_page_with_valid_token(self):
        with captured_templates(self.app) as templates:
            response = self.client.get(url_for(
                'users_blueprint.reset_password',
                token=self.user.generate_password_reset_token(),
            ))

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(templates))
            template, context = templates[0]
            self.assertEqual('users/reset_password.html', template.name)

    def test_post_page_with_valid_token(self):
        new_password = secrets.token_hex(16)
        self.assertFalse(self.user.check_password(new_password))
        post_data = {
            'password': new_password,
            'confirm_password': new_password,
            'submit': True,
        }
        response = self.client.post(url_for(
            'users_blueprint.reset_password',
            token=self.user.generate_password_reset_token(),
        ), data=post_data)

        self.assertEqual(302, response.status_code)
        expected_redirect_url = url_for('users_blueprint.login', _external=True)
        self.assertEqual(expected_redirect_url, response.location)

        self.assertTrue(self.user.check_password(new_password))


class LogoutTests(UserMixin, ClientRequestsMixin):
    def test_logout(self):
        response = self.client.get(url_for('users_blueprint.logout'))

        self.assertEqual(302, response.status_code)
        expected_redirect_url = url_for('products_blueprint.products', _external=True)
        self.assertEqual(expected_redirect_url, response.location)


if __name__ == "__main__":
    unittest.main()
