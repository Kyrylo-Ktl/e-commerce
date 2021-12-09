from contextlib import contextmanager

from flask import template_rendered, url_for


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def login(client, email, password):
    return client.post(url_for('users_blueprint.login'), data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get(url_for('users_blueprint.logout'), follow_redirects=True)
