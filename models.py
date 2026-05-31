from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id                 = db.Column(db.Integer, primary_key=True)
    username           = db.Column(db.String(80), unique=True, nullable=False)
    email              = db.Column(db.String(120), unique=True, nullable=False)
    password_hash      = db.Column(db.String(256), nullable=False)
    reset_token        = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    clients            = db.relationship("Client", backref="user", lazy=True)


class Client(db.Model):
    __tablename__ = "clients"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), default="")
    phone      = db.Column(db.String(30), default="")
    company    = db.Column(db.String(120), default="")
    status     = db.Column(db.String(20), default="lead")   # lead | active | inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes      = db.relationship("Note", backref="client", lazy=True, cascade="all, delete-orphan")


class Note(db.Model):
    __tablename__ = "notes"
    id         = db.Column(db.Integer, primary_key=True)
    client_id  = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
