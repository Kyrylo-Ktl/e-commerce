"""Module with shell for running app commands"""

from flask.cli import FlaskGroup

from app import app
from shop.db import db

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    pass


@cli.command("drop_db")
def drop_db():
    db.drop_all()


if __name__ == "__main__":
    cli()
