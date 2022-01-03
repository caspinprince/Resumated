from web_app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__='User_Info'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=True)
    google_id = db.Column(db.String(64), unique=True, index=True, nullable=True)
    about_me = db.Column(db.String(1000))
    headline = db.Column(db.String(250))
    last_online = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, first_name, last_name, email, username, password=None, google_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password) if password is not None else None
        self.google_id = google_id

    def password_check(self, password):
        return check_password_hash(self.password_hash, password)

