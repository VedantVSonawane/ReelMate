from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    watchlist = db.relationship('Watchlist', backref='user', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    genres = db.Column(db.String(200))  # Stored as "Action|Comedy"
    overview = db.Column(db.Text)
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(500))
    platforms = db.Column(db.String(200)) # Stored as "Netflix|Prime"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genres': self.genres,
            'description': self.overview,
            'year': self.year,
            'poster_url': self.poster_url,
            'platforms': self.platforms
        }

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
