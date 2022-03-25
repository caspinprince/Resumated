from flask import Blueprint

bp = Blueprint("social", __name__, static_url_path="/static")
from web_app.social import routes
