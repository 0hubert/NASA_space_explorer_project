from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    nasa_id = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class APOD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    media_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MarsPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nasa_id = db.Column(db.String(100), unique=True, nullable=False)
    rover_name = db.Column(db.String(50), nullable=False)
    camera_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    earth_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NEO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    neo_reference_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    nasa_jpl_url = db.Column(db.String(500))
    absolute_magnitude_h = db.Column(db.Float)
    estimated_diameter_min = db.Column(db.Float)
    estimated_diameter_max = db.Column(db.Float)
    is_potentially_hazardous = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 