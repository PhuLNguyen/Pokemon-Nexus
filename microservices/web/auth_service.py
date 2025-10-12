from datetime import datetime
from flask import request, render_template, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from web.db_utils import create_app, get_current_user_email

# Initialize the Flask App and MongoDB connection for this service
app, mongo = create_app(__name__)
# The Auth Service will run on port 5000 (default for Gunicorn in the new docker-compose)

# --- Routes from original app.py (Authentication and Dashboard) ---

@app.route('/')
def index():
    """Serves the main application page."""
    # This route is usually served by Nginx or a dedicated UI microservice, 
    # but for simplicity, we keep it in the Auth service to provide the entry point.
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login and session creation."""
    if request.method == 'POST':
        # Data can come as JSON (API client) or form data (Web form)
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Missing email or password'}), 400

        user = mongo.db.players.find_one({"email": email})
        
        if user and check_password_hash(user['password'], password):
            session['user_email'] = email
            session.permanent = True # Ensure session is persistent
            return render_template('home.html')
        else:
            return redirect(url_for('index'))
    
    # GET request is typically handled by the frontend, so we return a simple error if API is hit
    return jsonify({'message': 'Method Not Allowed for GET'}), 405

@app.route('/register', methods=['POST'])
def register():
    """Handles user registration."""
    data = request.get_json() if request.is_json else request.form
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400
    
    if mongo.db.players.find_one({"email": email}):
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    
    # 1. Create Player Profile
    new_player = {
        "email": email,
        "password": hashed_password,
        "wins": 0,
        "losses": 0,
        "level": 1,
        "xp": 0,
        "created_at": datetime.now()
    }
    mongo.db.players.insert_one(new_player)
    
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Handles user logout and session cleanup."""
    session.pop('user_email', None)
    return jsonify({'message': 'Logout successful'}), 200

# --- Dashboard / Profile Route ---

@app.route('/api/dashboard', methods=['GET'])
def dashboard_stats():
    """Returns player stats for the dashboard view."""
    user_email = get_current_user_email()
    if not user_email:
        return jsonify({'message': 'Unauthorized'}), 401

    player = mongo.db.players.find_one({"email": user_email}, {"password": 0}) # Exclude password
    
    if player:
        # Convert ObjectId to string for JSON serialization
        player['_id'] = str(player['_id']) 
        
        stats = {
            'email': player['email'],
            'wins': player.get('wins', 0),
            'losses': player.get('losses', 0),
            'level': player.get('level', 1),
            'xp': player.get('xp', 0),
            'created_at': player['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(stats), 200
    
    return jsonify({'message': 'Player not found'}), 404

# Run the app directly for development/testing within the container
if __name__ == '__main__':
    from datetime import datetime
    app.run(host='0.0.0.0', port=5000)
