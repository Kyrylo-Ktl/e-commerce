"""Module with shell for running app commands"""

from app import app
from flask.cli import FlaskGroup

from shop.db import db
from shop.seed_db import seed_admin, seed_brands, seed_categories, seed_products

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    seed_admin()
    seed_brands()
    seed_categories()
    seed_products(250)


@cli.command("drop_db")
def drop_db():
    db.reflect()
    db.drop_all()


if __name__ == "__main__":
    cli()
