from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_socketio import SocketIO
from werkzeug.utils import import_string
import werkzeug
werkzeug.import_string = import_string
from flask_caching import Cache
from config import Config
from celery import Celery


login_manager = LoginManager()
login_manager.login_view = "auth.login"
db = SQLAlchemy()
moment = Moment()
migrate = Migrate(compare_type=True)
cache = Cache()
socketio = SocketIO(logger=True, engineio_logger=True)

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

from web_app import models


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'FileSystemCache', 'CACHE_THRESHOLD': 5000, 'CACHE_DIR': 'cache', "CACHE_DEFAULT_TIMEOUT": 3600})

    from web_app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from web_app.general import bp as general_bp
    app.register_blueprint(general_bp)

    from web_app.social import bp as social_bp
    app.register_blueprint(social_bp)

    from web_app.auth.oauth import blueprint as google_bp
    app.register_blueprint(google_bp, url_prefix="/signup_google")

    socketio.init_app(app)

    return app


from web_app import models
