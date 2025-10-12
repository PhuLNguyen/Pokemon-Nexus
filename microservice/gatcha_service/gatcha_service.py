from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from pymongo import MongoClient
import os
import uuid

app = Flask(__name__)
CORS(app)


# Helper: get MongoDB collection
def get_collection(name):
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://mongo:27017')
    db_name = os.environ.get('MONGO_DB', 'pokemon_db')
    client = MongoClient(mongo_url)
    db = client[db_name]
    return db[name]

# Helper: generate unique id
def gen_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

pokemon_coll = get_collection('pokemon')

GATCHA_POOL = [
    {"name": "Squirtle", "atk": 48, "def": 65, "hp": 44, "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png"},
    {"name": "Jigglypuff", "atk": 45, "def": 20, "hp": 115, "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/39.png"},
    {"name": "Snorlax", "atk": 110, "def": 65, "hp": 160, "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png"}
]


@app.route('/gatcha', methods=['POST'])
def gatcha():
    data = request.get_json() or {}
    player = data.get('player')
    if not player:
        return jsonify({'message': 'player required'}), 400
    pick = random.choice(GATCHA_POOL)
    p_id = gen_id('pk')
    pokemon = {
        'id': p_id,
        'player': player,
        'name': pick['name'],
        'atk': pick['atk'],
        'def': pick['def'],
        'hp': pick['hp'],
        'locked': False,
        'image': pick['image']
    }
    pokemon_coll.insert_one(pokemon)
    return jsonify({'message': 'gatcha successful', 'new_pokemon': pokemon}), 201


if __name__ == '__main__':
    app.run(port=5002, debug=True)
