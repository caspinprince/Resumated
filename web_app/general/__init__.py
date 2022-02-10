from web_app.general import routes
from flask import Blueprint

bp = Blueprint("general", __name__, static_url_path="/static")
