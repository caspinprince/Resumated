import uuid
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from web_app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Connection(db.Model):
    __tablename__ = 'Connection'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    pending = db.Column(db.Boolean, nullable=False)
    userid1 = db.Column(
        db.Integer(),
        db.ForeignKey('User_Info.id'),
        nullable=False,
        primary_key=True,
    )
    userid2 = db.Column(
        db.Integer(),
        db.ForeignKey('User_Info.id'),
        nullable=False,
        primary_key=True,
    )
    user1 = db.relationship(
        "User",
        primaryjoin="Connection.userid1 == User_Info.c.id",
    )
    user2 = db.relationship(
        "User",
        primaryjoin="Connection.userid2 == User_Info.c.id"
    )


class FileAssociation(db.Model):
    __tablename__ = "FileAssociation"
    user_id = db.Column(db.Integer, db.ForeignKey("User_Info.id", ondelete='CASCADE'), primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("File.id", ondelete='CASCADE'), primary_key=True)
    user_status = db.Column(db.String(50), nullable=False)
    request_status = db.Column(db.String(25), nullable=True)
    requests = db.Column(db.String(2000), nullable=True)
    user = db.relationship("User", back_populates="files")
    file = db.relationship("File", back_populates="users")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = "User_Info"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=True)
    google_id = db.Column(db.String(64), unique=True, index=True, nullable=True)
    about_me = db.Column(db.String(1000), default="")
    headline = db.Column(db.String(250), default="")
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_online = db.Column(db.DateTime, default=datetime.utcnow)
    pfp_id = db.Column(db.String(50), unique=True)
    files = db.relationship(FileAssociation, back_populates="user", cascade="all, delete-orphan")
    settings = db.relationship("Settings", backref="users", cascade="all, delete-orphan")
    connections = db.relationship(
        Connection,
        primaryjoin=db.or_(
            id == Connection.userid1,
            id == Connection.userid2,
        ),
        viewonly=True,
        lazy='dynamic'
    )

    def __init__(
            self, first_name, last_name, email, username, password=None, google_id=None
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password_hash = (
            generate_password_hash(password) if password is not None else None
        )
        self.google_id = google_id
        self.pfp_id = uuid.uuid4()

    def password_check(self, password):
        return check_password_hash(self.password_hash, password)

    def get_connection(self, user, incoming=False):
        # filter for incoming connections only for accepting connections(cannot accept your own request)
        if incoming:
            return self.connections.filter(Connection.userid1 == user.id)
        return self.connections.filter((Connection.userid1 == user.id) | (Connection.userid2 == user.id))

    def connection_status(self, user):
        connection = self.get_connection(user)
        if connection.count() == 0:
            return "Not Connected"
        return 'Pending' if connection.first().pending else 'Connected'

    def connection_count(self):
        return self.connections.all().count()

    def request_connect(self, user):
        connection = Connection(user1=self, user2=user, pending=True)
        connection.connected, connection.connector = user, self
        db.session.add(connection)
        db.session.commit()

    def accept_connect(self, user):
        connection = self.get_connection(user, incoming=True).first()
        connection.pending=False
        db.session.add(connection)
        db.session.commit()

    def pending_connections(self, incoming=True):
        if incoming:
            return self.connections.filter(
                (Connection.userid2 == self.id) & (Connection.pending == True))
        return self.connections.filter(
            (Connection.userid1 == self.id) & (Connection.pending == True))

    def all_connections(self):
        return self.connections.filter_by(pending=False).all()


class File(db.Model):
    __tablename__ = "File"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("User_Info.id", ondelete='CASCADE'), nullable=False)
    users = db.relationship(
        FileAssociation, back_populates="file", cascade="all, delete-orphan"
    )
    feedback = db.relationship(
        "Feedback", lazy=True, backref="file", cascade="all, delete-orphan"
    )
    file_status = db.Column(db.String(25), nullable=False)


class Settings(db.Model):
    __tablename__ = "Settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User_Info.id", ondelete='CASCADE'), nullable=False)


class Feedback(db.Model):
    __tablename__ = "Feedback"
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("File.id", ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User_Info.id", ondelete='CASCADE'), primary_key=True)
    feedback = db.Column(db.String(10000), nullable=False)
