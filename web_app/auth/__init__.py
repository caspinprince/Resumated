from flask import Blueprint
bp=Blueprint('auth', __name__)
from web_app.auth import routes