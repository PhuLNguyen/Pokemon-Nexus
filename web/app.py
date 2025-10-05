from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # Recommended for real apps
from bson.objectid import ObjectId # Import for converting string IDs back to ObjectId
import os
import random
from datetime import datetime

# --- 1. SETUP AND CONFIGURATION ---

app = Flask(__name__)
# Enable CORS for the client running on a different port/origin
CORS(app) 

app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/fallback_db")
app.secret_key = os.getenv("SECRET_KEY", "a_development_fallback_key") 

# Initialize Flask-PyMongo
mongo = PyMongo(app)

# The 'players' collection will be accessed as mongo.db.players

# --- 2. ROUTES FOR USER INTERACTION ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main page with login/register forms."""
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """Handles the form submission from the Registration form and stores data in MongoDB."""
    
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('index'))

    # Check if user already exists (Read operation)
    existing_user = mongo.db.players.find_one({'email': email})
    if existing_user:
        flash('Email already registered. Please log in.', 'error')
        return redirect(url_for('index'))

    # Store user data (Create operation)
    try:
        # In a real app, use generate_password_hash for security:
        # hashed_password = generate_password_hash(password, method='sha256')
        
        user_data = {
            "email": email,
            "password": password # ⚠️ DANGER: Replace with hashed password in production
        }
        
        # Insert the new document into the 'players' collection
        mongo.db.players.insert_one(user_data)
        
        flash(f'Account created for {email}! Please log in.', 'success')
        
    except Exception as e:
        flash(f'An error occurred during registration: {e}', 'error')

    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    """Handles the form submission from the Login form and retrieves data from MongoDB."""
    
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('Both email and password are required for login.', 'error')
        return redirect(url_for('index'))

    # Retrieve user data (Read operation)
    user = mongo.db.players.find_one({'email': email})

    if user:
        # Check if the retrieved password matches the submitted password
        # In a real app, use: if check_password_hash(user['password'], password):
        if user['password'] == password: # ⚠️ DANGER: Replace with bcrypt check in production
            flash(f'Successfully logged in as {email}!', 'success')
            # Set a session variable to keep the user logged in
            session['email'] = email   
            # session.pop('email', None) # To log out, remove the session variable
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    else:
        # If no user is found with that email
        flash('Invalid email or password.', 'error')

    return redirect(url_for('index'))

@app.route('/home')
def home():
    # A page the user sees after a successful login
    return render_template('home.html')

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Returns a list of all Pokemon in the player inventory."""
    inventory = list(mongo.db.pokemon.find({'player': session['email']}))
    return jsonify(inventory)

@app.route('/api/release', methods=['DELETE'])
def release_pokemon():
    """Deletes multiple Pokemon documents based on their unique IDs."""
    data = request.get_json()
    pokemon_ids_to_release = data.get('ids', [])

    if not pokemon_ids_to_release:
        return jsonify({"message": "No Pokemon IDs provided for release."}), 400

    # Convert string IDs back to MongoDB ObjectId objects
    object_ids = [ObjectId(p_id) for p_id in pokemon_ids_to_release]
    
    # Use $in operator to find all documents whose _id is in the list
    result = mongo.db.pokemon.delete_many({
        '_id': {'$in': object_ids}
    })

    return jsonify({
        "message": f"Successfully released {result.deleted_count} Pokemon!",
        "deleted_count": result.deleted_count
    })

@app.route('/api/gatcha', methods=['POST'])
def run_gatcha():
    """Pulls a random Pokemon and adds it to the inventory."""
    
    # Define a pool of possible gatcha pulls
    # Add the player's email to associate the Pokemon with the user

    gatcha_pool = [
        {"player":session["email"], "name": "Squirtle", "atk": 48, "def": 65, "hp": 44, "locked":False, "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png"},
        {"player":session["email"], "name": "Jigglypuff", "atk": 45, "def": 20, "hp": 115, "locked":False, "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/39.png"},
        {"player":session["email"], "name": "Snorlax", "atk": 110, "def": 65, "hp": 160, "locked":False, "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png"}
    ]
    
    new_pokemon = random.choice(gatcha_pool)

    # Save the new Pokemon to the database
    mongo.db.pokemon.insert_one(new_pokemon)

    # Return the newly caught Pokemon data
    return jsonify({"message": "Gatcha successful!", "new_pokemon": new_pokemon})

@app.route('/api/battle', methods=['GET'])
def get_battle_queue():
    """Returns placeholder data for the battle queue."""
    return jsonify({
        "status": "In Queue",
        "position": random.randint(1, 10),
        "message": "Searching for opponents..."
    })

@app.route('/api/trade', methods=['GET'])
def get_trade_menu_data():
    """Returns the current player's inventory and all pending trades."""
    # 1. Get current player's available (unlocked) inventory
    available_inventory = []
    for doc in mongo.db.pokemon.find({"player": session['email'], "locked": False}):
        doc['id'] = str(doc.pop('_id')) 
        available_inventory.append(doc)
    
    # 2. Get all pending trades
    pending_trades = []
    for doc in mongo.db.trade.find({"status": "pending"}):
        doc['id'] = str(doc.pop('_id'))
        
        # Look up the details of the offered pokemon (for display)
        offered_pokemon_details = []
        for p_id in doc['offering_ids']:
            p_doc = mongo.db.pokemon.find_one({'_id': ObjectId(p_id)})
            if p_doc:
                offered_pokemon_details.append({"name": p_doc['name'], "image": p_doc['image']})
        
        doc['offered_details'] = offered_pokemon_details
        pending_trades.append(doc)

    return jsonify({
        "inventory": available_inventory,
        "pending_trades": pending_trades,
        "current_player": session['email']
    })


@app.route('/api/trade/create', methods=['POST'])
def create_trade():
    """Locks selected Pokemon and creates a new trade request."""
    data = request.get_json()
    offering_ids = data.get('offering_ids', [])
    looking_for_count = data.get('looking_for_count')

    if not offering_ids or looking_for_count is None or looking_for_count < 1:
        return jsonify({"message": "Invalid trade data."}), 400

    object_ids = [ObjectId(p_id) for p_id in offering_ids]
    
    # 1. Lock the Pokemon for trade
    lock_result = mongo.db.pokemon.update_many(
        {'_id': {'$in': object_ids}, 'player': session['email'], 'locked': False},
        {'$set': {'locked': True}}
    )

    if lock_result.modified_count != len(object_ids):
        # This handles if some were already locked or didn't belong to the player
        return jsonify({"message": "Could not lock all selected Pokemon. Operation aborted."}), 409

    # 2. Create the trade request document
    trade_request = {
        "creator": session['email'],
        "offering_ids": offering_ids, # Store as strings for easier retrieval
        "looking_for_count": looking_for_count,
        "status": "pending",
        "timestamp": datetime.now()
    }
    mongo.db.trade.insert_one(trade_request)
    
    return jsonify({
        "message": f"Trade request created! {len(offering_ids)} Pokemon locked.",
        "locked_count": lock_result.modified_count
    })


@app.route('/api/trade/fulfill', methods=['POST'])
def fulfill_trade():
    """Swaps ownership and removes the trade request."""
    data = request.get_json()
    trade_id = data.get('trade_id')
    fulfilling_ids = data.get('fulfilling_ids', [])

    if not trade_id or not fulfilling_ids:
        return jsonify({"message": "Missing trade ID or fulfilling Pokemon IDs."}), 400

    trade_obj_id = ObjectId(trade_id)
    fulfilling_obj_ids = [ObjectId(p_id) for p_id in fulfilling_ids]
    
    # 1. Retrieve the trade request
    trade = mongo.db.trade.find_one({'_id': trade_obj_id})
    if not trade:
        return jsonify({"message": "Trade request not found."}), 404
        
    if len(fulfilling_ids) != trade['looking_for_count']:
        return jsonify({"message": "You must offer the exact number of Pokemon requested."}), 400

    # 2. Unlock/Swap: The items being offered in the *original* trade
    original_offering_obj_ids = [ObjectId(p_id) for p_id in trade['offering_ids']]
    
    # A. Original Creator (e.g., TrainerB) receives current_player's (TrainerA's) Pokemon
    mongo.db.pokemon.update_many(
        {'_id': {'$in': fulfilling_obj_ids}, 'player': session['email']},
        {'$set': {'player': trade['creator'], 'locked': False}}
    )
    
    # B. current_player (TrainerA) receives the Original Creator's (TrainerB's) Pokemon
    mongo.db.pokemon.update_many(
        {'_id': {'$in': original_offering_obj_ids}},
        {'$set': {'player': session['email'], 'locked': False}}
    )

    # 3. Delete the fulfilled trade request
    mongo.db.trade.delete_one({'_id': trade_obj_id})

    return jsonify({
        "message": "Trade successful! Pokémon swapped and ownership transferred.",
        "traded_in": trade['offering_ids'],
        "traded_out": fulfilling_ids
    })

if __name__ == '__main__':
    app.run(debug=True) # Setting debug=True enables auto-reloading during development