"""Module with mail entity and initialization and sending email functions"""

from flask import current_app
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
