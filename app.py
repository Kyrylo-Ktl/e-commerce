"""Module with app instance"""

from shop import create_app

app = create_app(config_name='development')
