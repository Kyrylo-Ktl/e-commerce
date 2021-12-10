import os
from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    """Base configuration"""

    # Path
    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shop')

    # Application
    APP_NAME = getenv('APP_NAME')
    SECRET_KEY = getenv('SECRET_KEY')

    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')


class ProductionConfig(Config):
    """Production configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""

    WTF_CSRF_ENABLED = True
    DEBUG = True

    APP_HOST = getenv('APP_HOST')
    APP_PORT = getenv('APP_PORT')
    SERVER_NAME = f'{APP_HOST}:{APP_PORT}'

    # Postgres service
    POSTGRES_DB_HOST = getenv('POSTGRES_DB_HOST')
    POSTGRES_DB_PORT = getenv('POSTGRES_DB_PORT')

    # Postgres database
    POSTGRES_DB_NAME = getenv('POSTGRES_DB_NAME')
    POSTGRES_DB_USER = getenv('POSTGRES_DB_USER')
    POSTGRES_DB_PASSWORD = getenv('POSTGRES_DB_PASSWORD')

    # Database uri
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://'
        f'{POSTGRES_DB_USER}:{POSTGRES_DB_PASSWORD}'
        f'@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_NAME}'
    )


class TestingConfig(Config):
    """Testing configuration"""

    WTF_CSRF_ENABLED = False
    DEBUG = False
    TESTING = True

    # Database uri
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config.BASE_DIR, 'test.db')
