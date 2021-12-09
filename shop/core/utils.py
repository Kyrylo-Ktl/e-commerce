import os
from random import randint
import secrets

from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from PIL import Image


def get_random_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def make_random_filename(filename: str, directory: str = None) -> str:
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(filename)

    random_filename = os.path.join(directory or '', random_hex + file_ext)
    return random_filename


def create_random_image(save_path: str, size: tuple):
    image = Image.new('RGB', size, get_random_color())
    image.save(save_path)


def save_picture(form_picture, model) -> str:
    save_filename = make_random_filename(form_picture.filename, model.IMAGE_DIR)
    picture_path = os.path.join(current_app.root_path, 'static', save_filename)

    picture = Image.open(form_picture)
    picture = picture.resize(model.IMAGE_SIZE)
    picture.save(picture_path)

    return save_filename


def generate_token(expires_sec: int = 1800, **token_data) -> str:
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    token = s.dumps(token_data).decode('utf-8')
    return token


def verify_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        token_data = s.loads(token)
    except Exception:
        return None
    return token_data
