import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

# Initialize App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here' # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, User, Movie, Watchlist
from recommendation import get_recommendations

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    # Fetch movies from DB for the "Taste Test"
    movies = Movie.query.all()
    # Get unique genres for filter (if needed, or just hardcode common ones)
    all_genres = set()
    for m in movies:
        if m.genres:
            all_genres.update(m.genres.split('|'))
    
    return render_template('index.html', movies=movies, genres=sorted(list(all_genres)))

@app.route('/recommend', methods=['POST'])
def recommend():
    selected_ids = request.form.getlist('movie_ids')
    mood = request.form.get('mood')
    
    selected_ids = [int(id) for id in selected_ids]
    
    # Pass the DB session or query object if needed, but our updated recommendation.py 
    # will handle fetching from DB (we need to update it next).
    # For now, let's assume get_recommendations will be updated to query the DB.
    recommendations = get_recommendations(selected_ids, mood=mood)
    
    return render_template('results.html', recommendations=recommendations)

# --- Auth Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/watchlist/add/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    if not Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first():
        entry = Watchlist(user_id=current_user.id, movie_id=movie_id)
        db.session.add(entry)
        db.session.commit()
        flash('Added to watchlist!')
    return redirect(request.referrer)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Auto-seed if empty (useful for first run)
        if not Movie.query.first():
            from seed_data import seed_db
            seed_db()
    app.run(debug=True)
else:
    # Production mode (Gunicorn)
    with app.app_context():
        db.create_all()
        # Auto-seed if empty
        if not Movie.query.first():
            from seed_data import seed_db
            seed_db()
