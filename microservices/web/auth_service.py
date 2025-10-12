import os
import redis
from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_session import Session # Import Session
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from datetime import datetime

# --- SETUP AND CONFIGURATION ---

app = Flask(__name__)

# --- Configuration ---
# Load configuration from environment variables defined in docker-compose.yaml
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret') 
app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE', 'redis')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Required for modern browsers
app.config['SESSION_COOKIE_SECURE'] = False # Use True in HTTPS production
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/fallback_db")

# Redis Configuration
SESSION_REDIS_URL = os.environ.get('SESSION_REDIS')
if app.config['SESSION_TYPE'] == 'redis' and SESSION_REDIS_URL:
    try:
        # Initialize the Redis client instance from the connection string
        app.config['SESSION_REDIS'] = redis.from_url(SESSION_REDIS_URL)
        print("Redis client initialized for sessions.")
    except Exception as e:
        print(f"Error initializing Redis client: {e}")
        app.config['SESSION_TYPE'] = 'filesystem' # Fallback

 # --- Initialize Extensions ---
# IMPORTANT: Enable CORS for all microservices, allowing credentials (cookies)
CORS(app, supports_credentials=True)

# Initialize Flask-PyMongo
mongo = PyMongo(app)

# Initialize Flask-Session
Session(app) 

# --- Global ---
LEVEL_UP_XP = 100

@app.route('/')
def index():
    """Serves the main application page."""
    # This route is usually served by Nginx or a dedicated UI microservice, 
    # but for simplicity, we keep it in the Auth service to provide the entry point.
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    """Handles the form submission from the Registration form and stores data in MongoDB."""
    
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('index'))

    # Check if user already exists (Read operation)
    existing_user = mongo.db.players.find_one({'email': email})
    if existing_user:
        flash('Email already registered. Please log in.', 'error')
        return redirect(url_for('index'))

    # Store user data (Create operation)
    try:
        # In a real app, use generate_password_hash for security:
        # hashed_password = generate_password_hash(password, method='sha256')
        
        user_data = {
            "email": email,
            "password": password, # ⚠️ DANGER: Replace with hashed password in production
            "level": 1,
            "xp": 0,
            "wins": 0,
            "losses": 0,
            "created_at": datetime.now()
        }
        
        # Insert the new document into the 'players' collection
        mongo.db.players.insert_one(user_data)
        
        flash(f'Account created for {email}! Please log in.', 'success')
        
    except Exception as e:
        flash(f'An error occurred during registration: {e}', 'error')

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the form submission from the Login form and retrieves data from MongoDB."""
    
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('Both email and password are required for login.', 'error')
        return redirect(url_for('index'))

    # Retrieve user data (Read operation)
    user = mongo.db.players.find_one({'email': email})

    if user:
        # Check if the retrieved password matches the submitted password
        # In a real app, use: if check_password_hash(user['password'], password):
        if user['password'] == password: # ⚠️ DANGER: Replace with bcrypt check in production
            flash(f'Successfully logged in as {email}!', 'success')
            # Set a session variable to keep the user logged in
            session['email'] = email   
            # session.pop('email', None) # To log out, remove the session variable
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    else:
        # If no user is found with that email
        flash('Invalid email or password.', 'error')

    return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
def logout():
    """Logs out the current user by clearing the session."""
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    # A page the user sees after a successful login
    return render_template('home.html')

# --- API Route: Get User Info ---

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """Returns the current player's level and XP."""
    user = mongo.db.players.find_one({'email': session.get('email')})
    if not user:
        return jsonify({"message": "User not found."}), 404
    
    app.logger.info(f"LOGGER User {user.get('email')} requested their info.")
    print(f"PRINT User {user.get('email')} requested their info.")

    return jsonify({
        "email": user.get('email', "email-placeholder"),
        "level": user.get('level', 1),
        "xp": user.get('xp', 0),
        "xp_to_next_level": LEVEL_UP_XP - user.get('xp', 0),
        "wins": user.get('wins', 0),
        "losses": user.get('losses', 0)
    })

# Run the app directly for development/testing within the container
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
