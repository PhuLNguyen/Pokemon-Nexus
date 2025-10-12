import os
import random
from math import ceil
from datetime import datetime
from bson.objectid import ObjectId
from flask import request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from web.db_utils import create_app, get_current_user_email
import redis

# Use a non-standard port 5001 for SocketIO service (as per typical deployment)
app, mongo = create_app(__name__)

# --- SocketIO Setup ---
# Retrieve Redis URL from environment variables via the db_utils shared setup
REDIS_URL = os.environ.get('SESSION_REDIS', 'redis://localhost:6379/1') 
socketio = SocketIO(
    app,
    cors_allowed_origins="*", # Allow all origins for microservice communication
    message_queue=REDIS_URL, # Use Redis as the message broker for scaling
)

# --- Global State for Battle Service (Queue) ---
BATTLE_QUEUE = []

# --- Helper Functions for Battle Simulation ---

def update_player_stats(user_name, is_winner, xp_gained):
    """Updates player profile (wins/losses, XP/Level) in MongoDB."""
    
    # Simple leveling formula: gain 1 level for every 1000 total XP
    player = mongo.db.players.find_one({"email": user_name})
    if not player:
        return 0, 0
    
    current_xp = player.get('xp', 0)
    current_level = player.get('level', 1)
    
    # Calculate new total XP and level
    total_xp = current_xp + xp_gained
    new_level = 1 + int(total_xp / 1000)
    new_xp = total_xp % 1000

    level_increase = new_level - current_level
    
    update_fields = {
        '$set': {
            'level': new_level, 
            'xp': new_xp,
        },
        '$inc': {
            'wins': 1 if is_winner else 0,
            'losses': 1 if not is_winner else 0
        }
    }
    mongo.db.players.update_one({"email": user_name}, update_fields)
    
    return xp_gained, level_increase

def simulate_battle(player_mon, opponent_mon):
    """Simulates the battle based on ATK/DEF, returns battle result dictionary."""
    
    p1 = {"doc": player_mon, "hp": player_mon['hp'], "email": player_mon['owner_email']}
    p2 = {"doc": opponent_mon, "hp": opponent_mon['hp'], "email": opponent_mon['owner_email']}
    
    p1_atk = p1['doc']['atk']
    p2_atk = p2['doc']['atk']

    # Determine who attacks first (higher ATK stat)
    attacker = p1 if p1_atk >= p2_atk else p2
    defender = p2 if p1_atk >= p2_atk else p1
    
    battle_log = []
    
    # Battle loop (max 20 rounds to prevent infinite loop)
    for i in range(20):
        if p1['hp'] <= 0 or p2['hp'] <= 0:
            break
            
        defender_def = defender['doc']['def']
        # Damage calculation: simplified ATK - DEF/2
        damage = max(1, attacker['doc']['atk'] - ceil(defender_def / 2)) 
        
        defender['hp'] -= damage
        
        battle_log.append(f"{attacker['doc']['name']} attacks {defender['doc']['name']} for {damage} damage. {defender['doc']['name']} HP: {max(0, defender['hp'])}")
        
        # Swap attacker/defender roles
        attacker, defender = defender, attacker

    winner = p1 if p1['hp'] > p2['hp'] else p2
    loser = p2 if p1['hp'] > p2['hp'] else p1
    
    # XP calculation (simplified)
    xp_gained = random.randint(500, 1500)
    
    return {
        'winner_email': winner['email'],
        'loser_email': loser['email'],
        'winner_mon': winner['doc'],
        'loser_mon': loser['doc'],
        'xp_gained': xp_gained,
        'log': battle_log
    }

# --- SocketIO Event Handlers ---

@socketio.on('join_queue')
def handle_join_queue():
    """Handles a user requesting to join the matchmaking queue."""
    user_email = get_current_user_email()
    if not user_email:
        emit('queue_error', {'message': 'Authentication required. Please log in.'})
        return

    # 1. Get user's battle monster (simplest for now: grab the first one)
    user_mon_doc = mongo.db.inventory.find_one({"owner_email": user_email})
    if not user_mon_doc:
        emit('queue_error', {'message': 'You need at least one monster to battle!'})
        return
        
    user_mon_doc['_id'] = str(user_mon_doc['_id'])
    
    # 2. Check for existing queue entry
    existing_entry = next((item for item in BATTLE_QUEUE if item["email"] == user_email), None)

    if not existing_entry:
        # 3. Create queue entry
        entry = {
            "email": user_email,
            "sid": request.sid, # Store the current session ID
            "monster": user_mon_doc,
            "joined_at": datetime.now()
        }
        BATTLE_QUEUE.append(entry)
        app.logger.info(f"User {user_email} joined the queue. Current size: {len(BATTLE_QUEUE)}")

    # 4. Attempt to match (simple FIFO)
    opponent_entry = None
    if len(BATTLE_QUEUE) > 1:
        # Look for the oldest entry that isn't the current user
        for i, queued_user in enumerate(BATTLE_QUEUE):
            if queued_user['email'] != user_email:
                opponent_entry = BATTLE_QUEUE.pop(i) # Remove opponent
                # Ensure current user is removed if they were added in this request
                if not existing_entry: 
                    BATTLE_QUEUE.pop(-1) 
                break 

    if opponent_entry:
        
        # --- Run Battle Simulation ---
        result = simulate_battle(entry['monster'], opponent_entry['monster'])
        
        # --- Update DB (XP, Wins/Losses) ---
        # Update winner's stats
        xp_w, level_w = update_player_stats(result['winner_email'], is_winner=True, xp_gained=result['xp_gained'])
        # Update loser's stats
        update_player_stats(result['loser_email'], is_winner=False, xp_gained=0) # Losers gain no XP in this setup
        
        # Prepare results for the current user and the opponent
        user_is_winner = result['winner_email'] == user_email
        opponent_is_winner = result['winner_email'] == opponent_entry['email']

        client_result = {
            'status': 'complete',
            'winner_email': result['winner_email'],
            'winner_mon_name': result['winner_mon']['name'],
            'loser_mon_name': result['loser_mon']['name'],
            'xp_gained': xp_w if user_is_winner else 0,
            'log': result['log'],
            'is_winner': user_is_winner
        }
        opponent_client_result = {
            'status': 'complete',
            'winner_email': result['winner_email'],
            'winner_mon_name': result['winner_mon']['name'],
            'loser_mon_name': result['loser_mon']['name'],
            'xp_gained': xp_w if opponent_is_winner else 0,
            'log': result['log'],
            'is_winner': opponent_is_winner
        }
        
        # Emit results to both clients
        emit('battle_result', client_result, room=request.sid)
        socketio.emit('battle_result', opponent_client_result, room=opponent_entry['sid'])
        
        app.logger.info(f"Battle completed between {user_email} and {opponent_entry['email']}. Winner: {result['winner_email']}")
        
    else:
        # No match found, notify the user of their queue position
        position = BATTLE_QUEUE.index(entry) + 1
        emit('queue_update', {'position': position})
        app.logger.info(f"User {user_email} added to queue, position {position}")


@socketio.on('disconnect')
def handle_disconnect():
    """Removes the user from the queue upon disconnect."""
    user_email = get_current_user_email()
    if user_email:
        global BATTLE_QUEUE
        # Find and remove the user from the queue
        BATTLE_QUEUE = [item for item in BATTLE_QUEUE if item.get('email') != user_email]
        app.logger.info(f"User {user_email} disconnected and removed from queue.")

@app.route('/api/battle/data', methods=['GET'])
def get_battle_selection_data():
    """Placeholder route to get monster selection data before joining queue."""
    user_email = get_current_user_email()
    if not user_email:
        return jsonify({'message': 'Unauthorized'}), 401

    # Fetch the player's monster list for selection (simplistic for now)
    inventory = mongo.db.inventory.find({"owner_email": user_email})
    monsters_list = [{
        'id': str(m['_id']), 
        'name': m['name'], 
        'level': m['level']
    } for m in inventory]
    
    return jsonify({'monsters': monsters_list}), 200


if __name__ == '__main__':
    # Run Flask-SocketIO with eventlet or gevent worker, or use socketio.run
    socketio.run(app, host='0.0.0.0', port=5001)
