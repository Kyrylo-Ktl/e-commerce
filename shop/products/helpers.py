import os
from random import randint
import secrets

from flask import current_app
from PIL import Image

from shop.products.models import ProductModel


def get_random_color():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def make_random_filename(filename: str):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(filename)
    random_filename = os.path.join(ProductModel.IMAGE_DIR, random_hex + file_ext)
    return random_filename


def create_random_image(save_path: str, size: tuple):
    image = Image.new('RGB', size, get_random_color())
    image.save(save_path)


def save_product_picture(form_picture):
    save_filename = make_random_filename(form_picture.filename)
    picture_path = os.path.join(current_app.root_path, 'static', save_filename)

    picture = Image.open(form_picture)
    picture = picture.resize(ProductModel.IMAGE_SIZE)
    picture.save(picture_path)

    return save_filename
