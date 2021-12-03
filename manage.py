"""Module with shell for running app commands"""

from app import app
from flask.cli import FlaskGroup

from shop.db import db
from shop.seed_db import seed_admin, seed_brands, seed_categories, seed_orders, seed_products, seed_users

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    seed_brands(n_brands=12)
    seed_categories(n_categories=12)
    seed_products(n_products=500)
    seed_users(n_users=25)
    seed_orders(n_orders=90)
    seed_admin()


@cli.command("drop_db")
def drop_db():
    db.reflect()
    db.drop_all()


if __name__ == "__main__":
    cli()
