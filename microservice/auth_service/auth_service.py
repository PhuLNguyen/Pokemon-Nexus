from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret')

# Flask-Session config (use redis when provided)
app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE', 'redis')
if os.environ.get('SESSION_REDIS'):
    app.config['SESSION_REDIS'] = os.environ.get('SESSION_REDIS')
Session(app)


# Helper: get MongoDB collection
def get_collection(name):
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://mongo:27017')
    db_name = os.environ.get('MONGO_DB', 'pokemon_db')
    client = MongoClient(mongo_url)
    db = client[db_name]
    return db[name]

# Helper: current UTC time
def now():
    return datetime.utcnow().isoformat()

players = get_collection('players')


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
    app.run(port=5000, debug=True)
