import random
from datetime import datetime
from flask import request, jsonify
from web.db_utils import create_app, get_current_user_email

# Initialize the Flask App and MongoDB connection for this service
app, mongo = create_app(__name__)

# --- Core Monster Generation Logic (Moved from app.py) ---
def generate_monster_stats(base_name, level=1):
    """Generates base stats for a new monster based on provided level."""
    # Simplified stats for a random monster
    return {
        'name': base_name,
        'species': base_name.split('-')[0],
        'level': level,
        'hp': random.randint(30, 50) + level * 5,
        'atk': random.randint(10, 20) + level * 2,
        'def': random.randint(10, 20) + level * 2,
        'xp': 0,
        'created_at': datetime.now()
    }

def get_random_monster_name():
    """Returns a random monster name from a predefined list (simplified)."""
    monsters = ["Ignis", "Aqua", "Terra", "Aero", "Lumen", "Umbra", "Bolt"]
    suffix = ["Jr", "S", "Alpha", "Omega", "Max"]
    return f"{random.choice(monsters)}-{random.choice(suffix)}"

# --- Routes ---

@app.route('/api/gatcha', methods=['GET'])
def run_gatcha():
    """This endpoint is no longer available. Use POST instead."""
    return jsonify({'message': 'Method Not Allowed'}), 405

@app.route('/api/gatcha/', methods=['POST'])
def run_gatcha_post():
    """Simulates a monster draw and adds it to the user's inventory.

    Note: This endpoint accepts POST requests and uses the trailing-slash
    path to match the Nginx proxy configuration which proxies `/api/gatcha/`.
    """
    user_email = get_current_user_email()
    if not user_email:
        return jsonify({'message': 'Unauthorized'}), 401

    # Logic: Draw a new monster at level 1
    new_monster_name = get_random_monster_name()
    new_monster = generate_monster_stats(new_monster_name, level=1)
    new_monster['owner_email'] = user_email

    # Save to inventory collection and attach the inserted id to the response
    result = mongo.db.inventory.insert_one(new_monster)
    new_monster['_id'] = str(result.inserted_id)

    return jsonify({
        'message': f"Congratulations! You drew a {new_monster['name']}!",
        'monster': new_monster
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
