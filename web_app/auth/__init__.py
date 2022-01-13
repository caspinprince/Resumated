from flask import Blueprint
bp=Blueprint('auth', __name__, template_folder="templates", static_folder='static')
from web_app.auth import routes