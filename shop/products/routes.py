"""Module with products blueprint routes"""

from flask import Blueprint

from shop.products.views import (
    brand_update,
    category_update,
    create_brand,
    create_category,
    create_product,
    product_detail,
    product_update,
    products
)

products_blueprint = Blueprint('products_blueprint', __name__)

products_blueprint.add_url_rule('/',
                                view_func=products, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/products',
                                view_func=products, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/product_detail/<int:product_id>',
                                view_func=product_detail, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/product_update/<int:product_id>',
                                view_func=product_update, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/create_brand',
                                view_func=create_brand, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/brand_update/<int:brand_id>',
                                view_func=brand_update, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/create_category',
                                view_func=create_category, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/category_update/<int:category_id>',
                                view_func=category_update, methods=['GET', 'POST'])
products_blueprint.add_url_rule('/create_product',
                                view_func=create_product, methods=['GET', 'POST'])
