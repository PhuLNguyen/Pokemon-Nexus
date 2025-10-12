
from flask import Flask, session, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_session import Session
from pymongo import MongoClient
import os
import os
import random
from math import ceil

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret')

# Configure Flask-Session to use Redis when available
app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE', 'redis')
app.config['SESSION_REDIS'] = None
if os.environ.get('SESSION_REDIS'):
    app.config['SESSION_REDIS'] = os.environ.get('SESSION_REDIS')

Session(app)

# SocketIO message queue (use REDIS if provided)
message_queue = os.environ.get('SOCKETIO_MESSAGE_QUEUE') or os.environ.get('SESSION_REDIS')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet', message_queue=message_queue)

BATTLE_QUEUE = []


# Helper: get MongoDB collection
def get_collection(name):
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://mongo:27017')
    db_name = os.environ.get('MONGO_DB', 'pokemon_db')
    client = MongoClient(mongo_url)
    db = client[db_name]
    return db[name]

pokemon_coll = get_collection('pokemon')

def simulate_battle(player_mon, opponent_mon):
    p1 = {"doc": player_mon, "hp": player_mon['hp']}
    p2 = {"doc": opponent_mon, "hp": opponent_mon['hp']}
    p1_atk = p1['doc']['atk']
    p2_atk = p2['doc']['atk']
    attacker = p1 if p1_atk >= p2_atk else p2
    defender = p2 if p1_atk >= p2_atk else p1
    for _ in range(20):
        if p1['hp'] <= 0 or p2['hp'] <= 0:
            break
        defender_def = defender['doc']['def']
        damage = max(1, attacker['doc']['atk'] - ceil(defender_def / 2))
        defender['hp'] -= damage
        attacker, defender = defender, attacker
    return p1['hp'] > 0

@socketio.on('connect')
def handle_connect():
    app.logger.info(f'Client connected: sid={request.sid}')

@socketio.on('join_queue')
def handle_join_queue(data=None):
    player = data.get('player') if data else None
    sid = request.sid
    if any(p['sid'] == sid for p in BATTLE_QUEUE):
        return
    BATTLE_QUEUE.append({'player': player, 'sid': sid})
    if len(BATTLE_QUEUE) >= 2:
        p1 = BATTLE_QUEUE.pop(0)
        p2 = BATTLE_QUEUE.pop(0)
        p1_mon_docs = [m for m in pokemon_coll.find({'player': p1['player']}) if not m.get('locked')]
        p2_mon_docs = [m for m in pokemon_coll.find({'player': p2['player']}) if not m.get('locked')]
        if not p1_mon_docs or not p2_mon_docs:
            emit('queue_error', {'message': 'Not enough available Pokemon to battle!'}, room=p1['sid'])
            return
        p1_mon = random.choice(p1_mon_docs)
        p2_mon = random.choice(p2_mon_docs)
        is_p1_winner = simulate_battle(p1_mon, p2_mon)
        winner = p1['player'] if is_p1_winner else p2['player']
        for player in [p1, p2]:
            is_winner = player['player'] == winner
            payload = {
                'status': 'complete',
                'message': f"Battle finished! {'WIN' if is_winner else 'LOSS'}",
                'result': {
                    'player_mon': p1_mon['name'] if player['player'] == p1['player'] else p2_mon['name'],
                    'opponent_mon': p2_mon['name'] if player['player'] == p1['player'] else p1_mon['name'],
                    'result_message': 'WIN' if is_winner else 'LOSS'
                }
            }
            socketio.emit('battle_result', payload, room=player['sid'])

@socketio.on('disconnect')
def handle_disconnect():
    global BATTLE_QUEUE
    BATTLE_QUEUE = [p for p in BATTLE_QUEUE if p['sid'] != request.sid]

if __name__ == '__main__':
    socketio.run(app, port=5004, debug=True)
