from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_cors import CORS
from flask_session import Session
from pymongo import MongoClient
from datetime import datetime
import os
import redis as _redis

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret')

# Flask-Session config (use redis when provided)
app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE', 'redis')
app.config['SESSION_REDIS'] = None
if os.environ.get('SESSION_REDIS'):
    # If SESSION_REDIS is a URL (e.g. redis://redis:6379/1) create a client
    try:
        app.config['SESSION_REDIS'] = _redis.from_url(os.environ.get('SESSION_REDIS'))
    except Exception:
        # Fallback to raw value if creating the client fails (older Flask-Session may accept it)
        app.config['SESSION_REDIS'] = os.environ.get('SESSION_REDIS')
Session(app)


# Helper: get MongoDB collection
def get_collection(name):
    # Prefer MONGO_URI (used in docker-compose), fall back to MONGO_URL, then default to
    # the compose service name 'mongodb' so the container can resolve it.
    mongo_url = os.environ.get('MONGO_URI') or os.environ.get('MONGO_URL') or 'mongodb://mongodb:27017'
    db_name = os.environ.get('MONGO_DB', 'pokemon_db')
    # Set a reasonable server selection timeout so failures surface quickly
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    return db[name]

# Helper: current UTC time
def now():
    return datetime.utcnow().isoformat()

players = get_collection('players')


@app.route('/')
def home():
    return send_from_directory('.', 'login.html')

@app.route('/home')
def home_page():
    return send_from_directory('.', 'home.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'email and password required'}), 400
    existing = players.find_one({'email': email})
    if existing:
        return jsonify({'message': 'email already exists'}), 409
    user_doc = {
        'email': email,
        'password': password,
        'level': 1,
        'xp': 0,
        'wins': 0,
        'losses': 0,
        'created_at': now()
    }
    players.insert_one(user_doc)
    return jsonify({'message': 'registered', 'email': email}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    user = players.find_one({'email': email})
    if not user or user.get('password') != password:
        return jsonify({'message': 'invalid credentials'}), 401
    session['email'] = email
    return jsonify({'message': 'logged_in', 'email': email})


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return jsonify({'message': 'logged_out'})


@app.route('/user/info', methods=['GET'])
def user_info():
    email = session.get('email') or request.args.get('email')
    if not email:
        return jsonify({'message': 'not authenticated'}), 401
    user = players.find_one({'email': email})
    if not user:
        return jsonify({'message': 'user not found'}), 404
    return jsonify({
        'email': user.get('email'),
        'level': user.get('level', 1),
        'xp': user.get('xp', 0),
        'wins': user.get('wins', 0),
        'losses': user.get('losses', 0)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
