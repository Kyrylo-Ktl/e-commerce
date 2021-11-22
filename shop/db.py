"""Module with database entity and initialization function"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_database(app):
    db.init_app(app)
    db.create_all()
    db.session.commit()
