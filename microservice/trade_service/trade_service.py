from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import uuid
from datetime import datetime

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

# Helper: current UTC time
def now():
    return datetime.utcnow().isoformat()

trades = get_collection('trade')
pokemon = get_collection('pokemon')


@app.route('/trades', methods=['GET'])
def list_trades():
    pending = trades.find({'status': 'pending'})
    return jsonify(pending)


@app.route('/trade/create', methods=['POST'])
def create_trade():
    data = request.get_json() or {}
    creator = data.get('creator')
    offering_ids = data.get('offering_ids', [])
    if not creator or len(offering_ids) != 1:
        return jsonify({'message': 'creator and exactly one offering_id required'}), 400
    # lock the pokemon
    p_id = offering_ids[0]
    p = pokemon.find_one({'id': p_id})
    if not p or p['player'] != creator or p.get('locked'):
        return jsonify({'message': 'cannot lock pokemon'}), 409
    pokemon.update_one({'id': p_id}, {'$set': {'locked': True}})
    trade_id = gen_id('tr')
    trades.insert_one({
        'id': trade_id,
        'creator': creator,
        'offering_ids': offering_ids,
        'looking_for_count': 1,
        'status': 'pending',
        'timestamp': now()
    })
    return jsonify({'message': 'trade created', 'trade_id': trade_id}), 201


@app.route('/trade/fulfill', methods=['PUT'])
def fulfill_trade():
    data = request.get_json() or {}
    trade_id = data.get('trade_id')
    fulfiller = data.get('fulfiller')
    fulfilling_ids = data.get('fulfilling_ids', [])
    if not trade_id or len(fulfilling_ids) != 1 or not fulfiller:
        return jsonify({'message': 'trade_id, fulfiller and exactly one fulfilling_id required'}), 400
    trade = trades.find_one({'id': trade_id})
    if not trade or trade['looking_for_count'] != 1 or trade['status'] != 'pending':
        return jsonify({'message': 'trade not found or not fulfillable'}), 404
    original_offered_id = trade['offering_ids'][0]
    fulfilling_id = fulfilling_ids[0]
    if not pokemon.find_one({'id': fulfilling_id}):
        return jsonify({'message': 'fulfilling pokemon not found'}), 404
    # transfer ownership
    pokemon.update_one({'id': fulfilling_id}, {'$set': {'player': trade['creator'], 'locked': False}})
    pokemon.update_one({'id': original_offered_id}, {'$set': {'player': fulfiller, 'locked': False}})
    trades.update_one({'id': trade_id}, {'$set': {'status': 'fulfilled'}})
    return jsonify({'message': 'trade fulfilled', 'traded_in': original_offered_id, 'traded_out': fulfilling_id})


if __name__ == '__main__':
    app.run(port=5003, debug=True)
