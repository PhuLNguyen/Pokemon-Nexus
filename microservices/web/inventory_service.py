import json
from bson.objectid import ObjectId
from flask import request, jsonify
from web.db_utils import create_app, get_current_user_email

# Initialize the Flask App and MongoDB connection for this service
app, mongo = create_app(__name__)

# --- Helper to serialize MongoDB documents ---
def serialize_inventory(monster):
    """Converts a single MongoDB monster document to a JSON-safe dictionary."""
    if monster:
        monster['_id'] = str(monster['_id'])
    return monster

@app.route('/api/inventory/', methods=['GET'])
def get_inventory():
    """Retrieves all monsters owned by the current user."""
    user_email = get_current_user_email()

    # Fetch all monsters belonging to the user
    inventory = mongo.db.pokemon.find({"player": user_email})
    
    return jsonify(inventory)

@app.route('/api/release', methods=['POST'])
def release_monster():
    """Allows a user to release (delete) a monster from their inventory."""
    user_email = get_current_user_email()
    if not user_email:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    monster_id_str = data.get('monster_id')

    if not monster_id_str:
        return jsonify({'message': 'Missing monster_id'}), 400
    
    try:
        # MongoDB requires ObjectId for lookup
        monster_id = ObjectId(monster_id_str)
    except:
        return jsonify({'message': 'Invalid Monster ID format'}), 400

    # Ensure the monster belongs to the user and then delete it
    result = mongo.db.inventory.delete_one({
        "_id": monster_id, 
        "player": user_email
    })

    if result.deleted_count == 1:
        return jsonify({'message': 'Monster released successfully'}), 200
    else:
        # Could be not found or not owned by the user
        return jsonify({'message': 'Monster not found or you do not own it'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # Microservices run on default 5000 internally
