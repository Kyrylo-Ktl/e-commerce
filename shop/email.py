"""Module with mail entity and initialization and sending email functions"""

from flask import current_app, render_template, url_for
from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    mail.init_app(app)


def send_mail(send_to: list, subject: str, html: str):
    msg = Message(
        subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=send_to,
    )
    msg.html = html
    mail.send(msg)


def send_token_url_mail(email, subject, token, url, template):
    token_url = url_for(url, token=token, _external=True)
    html = render_template(f'email/{template}.html', token_url=token_url)
    send_mail(send_to=[email], subject=subject, html=html)
