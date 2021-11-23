"""Module with core blueprint and its routes"""

from flask import Blueprint, render_template

core_blueprint = Blueprint('core_blueprint', __name__)


@core_blueprint.route('/', methods=['GET', 'POST'])
@core_blueprint.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')
