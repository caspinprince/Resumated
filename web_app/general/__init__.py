from flask import Blueprint
bp = Blueprint('general', __name__, template_folder='templates', static_folder='static')
from web_app.general import routes
