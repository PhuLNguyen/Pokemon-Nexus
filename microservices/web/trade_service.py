import json
from bson.objectid import ObjectId
from flask import request, jsonify
from web.db_utils import create_app, get_current_user_email
from datetime import datetime

# Initialize the Flask App and MongoDB connection for this service
app, mongo = create_app(__name__)

# --- Routes ---

@app.route('/api/trades', methods=['GET', 'POST'])
def handle_trades():
    user_email = get_current_user_email()
    if not user_email:
        return jsonify({'message': 'Unauthorized'}), 401

    # --- GET: List Open Trades ---
    if request.method == 'GET':
        # Find trades where status is 'open' and the user is not the creator
        trades = mongo.db.trades.find({
            "status": "open", 
            "creator_email": {"$ne": user_email}
        })
        
        trade_list = []
        for trade in trades:
            # Convert ObjectId to string for JSON serialization
            trade['_id'] = str(trade['_id'])
            trade_list.append(trade)
            
        return jsonify(trade_list), 200

    # --- POST: Create a New Trade ---
    elif request.method == 'POST':
        data = request.get_json()
        monster_id_str = data.get('monster_id')
        desired_monster_species = data.get('desired_species')

        if not monster_id_str or not desired_monster_species:
            return jsonify({'message': 'Missing monster_id or desired_species'}), 400

        try:
            monster_id = ObjectId(monster_id_str)
        except:
            return jsonify({'message': 'Invalid Monster ID format'}), 400

        # 1. Verify the user owns the monster and it's not already traded
        offered_monster = mongo.db.inventory.find_one({
            "_id": monster_id,
            "owner_email": user_email
        })

        if not offered_monster:
            return jsonify({'message': 'Offered monster not found or not owned'}), 404
        
        # 2. Create the trade offer
        new_trade = {
            "creator_email": user_email,
            "offered_monster_id": monster_id_str,
            "offered_monster_name": offered_monster['name'],
            "desired_species": desired_monster_species,
            "status": "open",
            "created_at": datetime.now()
        }
        
        # Temporarily mark the monster as 'in trade' to prevent it from being released or used elsewhere
        mongo.db.inventory.update_one(
            {"_id": monster_id},
            {"$set": {"status": "in_trade", "trade_id": new_trade['_id']}}
        )

        mongo.db.trades.insert_one(new_trade)
        new_trade['_id'] = str(new_trade['_id'])
        
        return jsonify({'message': 'Trade offer created successfully', 'trade': new_trade}), 201

@app.route('/api/trade/<trade_id>', methods=['POST'])
def fulfill_trade(trade_id):
    """Allows a user to accept and fulfill an open trade offer."""
    user_email = get_current_user_email()
    if not user_email:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    accepting_monster_id_str = data.get('accepting_monster_id')

    if not accepting_monster_id_str:
        return jsonify({'message': 'Missing accepting_monster_id'}), 400

    try:
        trade_obj_id = ObjectId(trade_id)
        accepting_monster_id = ObjectId(accepting_monster_id_str)
    except:
        return jsonify({'message': 'Invalid ID format'}), 400

    # 1. Check if the trade is open and not created by the current user
    trade = mongo.db.trades.find_one({"_id": trade_obj_id, "status": "open", "creator_email": {"$ne": user_email}})

    if not trade:
        return jsonify({'message': 'Trade not found, closed, or you are the creator'}), 404

    # 2. Verify the accepting user owns the monster they are offering
    accepting_monster = mongo.db.inventory.find_one({
        "_id": accepting_monster_id, 
        "owner_email": user_email,
        "status": {"$ne": "in_trade"}
    })
    
    if not accepting_monster:
        return jsonify({'message': 'Accepting monster not found, not owned, or is in another trade'}), 404
    
    # 3. Verify the accepting monster matches the desired species
    if accepting_monster.get('species') != trade['desired_species']:
        return jsonify({'message': f"Trade requires species: {trade['desired_species']}"}), 400
        
    # 4. Perform the trade (swapping ownership)
    
    # Get the offered monster (from the creator)
    offered_monster_id = ObjectId(trade['offered_monster_id'])
    
    # A. Update ownership of the monster offered by the creator (becomes new owner's)
    mongo.db.inventory.update_one(
        {"_id": offered_monster_id},
        {"$set": {"owner_email": user_email, "status": "traded", "trade_id": None}}
    )

    # B. Update ownership of the monster offered by the accepter (becomes creator's)
    mongo.db.inventory.update_one(
        {"_id": accepting_monster_id},
        {"$set": {"owner_email": trade['creator_email'], "status": "traded", "trade_id": None}}
    )

    # 5. Update trade status to closed
    mongo.db.trades.update_one(
        {"_id": trade_obj_id},
        {"$set": {"status": "closed", "accepter_email": user_email, "fulfilled_at": datetime.now()}}
    )

    return jsonify({'message': 'Trade fulfilled successfully!'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
