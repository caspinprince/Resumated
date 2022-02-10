from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from config import Config

login_manager = LoginManager()
login_manager.login_view = "auth.login"
db = SQLAlchemy()
moment = Moment()
migrate = Migrate(compare_type=True)
from web_app import models


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment.init_app(app)
    from web_app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from web_app.general import bp as general_bp

    app.register_blueprint(general_bp)

    from web_app.auth.oauth import blueprint as google_bp

    app.register_blueprint(google_bp, url_prefix="/signup_google")
    return app


from web_app import models
