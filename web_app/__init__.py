import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql
from flask_migrate import Migrate
login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from web_app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from web_app.general import bp as general_bp
app.register_blueprint(general_bp)

from web_app.auth.oauth import blueprint as google_bp
app.register_blueprint(google_bp, url_prefix='/signup_google')

login_manager.init_app(app)
login_manager.login_view = 'login'

