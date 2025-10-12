from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)


# Helper: get MongoDB collection
def get_collection(name):
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://mongo:27017')
    db_name = os.environ.get('MONGO_DB', 'pokemon_db')
    client = MongoClient(mongo_url)
    db = client[db_name]
    return db[name]

pokemon = get_collection('pokemon')


@app.route('/inventory', methods=['GET'])
def get_inventory():
    player = request.args.get('player')
    if not player:
        return jsonify({'message': 'player query param required'}), 400
    items = pokemon.find({'player': player})
    return jsonify(items)


@app.route('/release', methods=['DELETE'])
def release():
    data = request.get_json() or {}
    ids = data.get('ids', [])
    # For Mongo: expect list of string ids; fallback wrapper handles delete
    # If using real MongoDB, these would be ObjectId conversions; here we rely on 'id' field
    result = pokemon.delete_many({'_id': {'$in': ids}})
    return jsonify({'message': f'released {getattr(result, "deleted_count", 0)}', 'deleted_count': getattr(result, 'deleted_count', 0)})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
