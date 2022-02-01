from flask import Blueprint

bp = Blueprint("general", __name__)
from web_app.general import routes
