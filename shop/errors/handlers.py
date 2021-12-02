from flask import Blueprint, render_template

errors_blueprint = Blueprint('errors', __name__)


@errors_blueprint.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors_blueprint.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403
