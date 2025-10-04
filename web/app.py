from flask import Flask, request, render_template, redirect, url_for, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # Recommended for real apps
import os

# --- 1. SETUP AND CONFIGURATION ---

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/fallback_db")
app.secret_key = os.getenv("SECRET_KEY", "a_development_fallback_key") 

# Initialize Flask-PyMongo
mongo = PyMongo(app)

# The 'players' collection will be accessed as mongo.db.players

# --- 2. ROUTES FOR USER INTERACTION ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main page with login/register forms."""
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """Handles the form submission from the Registration form and stores data in MongoDB."""
    
    name = request.form.get('name')
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
            "name": name,
            "email": email,
            "password": password # ⚠️ DANGER: Replace with hashed password in production
        }
        
        # Insert the new document into the 'players' collection
        mongo.db.players.insert_one(user_data)
        
        flash(f'Account created for {email}! Please log in.', 'success')
        
    except Exception as e:
        flash(f'An error occurred during registration: {e}', 'error')

    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
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
            # You would typically set a session variable here
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    else:
        # If no user is found with that email
        flash('Invalid email or password.', 'error')

    return redirect(url_for('index'))


# --- 3. Example home and Run App ---

@app.route('/home')
def home():
    # A page the user sees after a successful login
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)