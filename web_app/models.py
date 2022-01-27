from web_app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class FileAssociation(db.Model):
    __tablename__ = 'FileAssociation'
    user_id = db.Column(db.Integer, db.ForeignKey('User_Info.id'), primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('File.id'), primary_key=True)
    user_status = db.Column(db.String(50), nullable=False)
    file_status = db.Column(db.String(25), nullable=False)
    user = db.relationship("User", back_populates="files")
    file = db.relationship("File", back_populates="users")


class User(db.Model, UserMixin):
    __tablename__='User_Info'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=True)
    google_id = db.Column(db.String(64), unique=True, index=True, nullable=True)
    about_me = db.Column(db.String(1000), default="")
    headline = db.Column(db.String(250), default="")
    last_online = db.Column(db.DateTime, default=datetime.utcnow)
    pfp_id = db.Column(db.String(50), unique=True)
    files = db.relationship(FileAssociation, back_populates='user')
    settings = db.relationship('Settings', lazy=True, backref='users')

    def __init__(self, first_name, last_name, email, username, password=None, google_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password) if password is not None else None
        self.google_id = google_id
        self.pfp_id = uuid.uuid4()

    def password_check(self, password):
        return check_password_hash(self.password_hash, password)

class File(db.Model):
    __tablename__='File'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)
    users = db.relationship(FileAssociation, back_populates='file')


class Settings(db.Model):
    __tablename__ = 'Settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User_Info.id'), nullable=False)




