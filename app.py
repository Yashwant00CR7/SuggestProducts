# //Deploy code 
import json
import os
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Load Firebase credentials from environment variables
firebase_config = json.loads(os.getenv("FIREBASE_CONFIG"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

# from flask import Flask, jsonify, request
# import firebase_admin
# from firebase_admin import credentials, firestore

# app = Flask(__name__)

# # Initialize Firebase
# cred = credentials.Certificate(r'temp/firebase_config.json')
# firebase_admin.initialize_app(cred)

# # Initialize Firestore DB
# db = firestore.client()

@app.route('/')
def home():
    return "Firebase Connected with Flask!"

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    doc_ref = db.collection('users').add(data)
    return jsonify({"status": "success", "id": str(doc_ref[1].id)})

@app.route('/get', methods=['GET'])
def get_and_update_data():
    user_id = request.args.get('userId')  # Get userId from request

    if not user_id:
        return jsonify({'status': 'failed', 'message': 'Missing userId'}), 400

    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify({'status': 'failed', 'message': 'User not found'}), 404

    user_data = user_doc.to_dict()

    # Check if the user is logged in
    if user_data.get('loggedIn', False):
        user_name = user_data.get('name', 'Unknown')
        suggested_products = [user_name]  # For now, just add the username

        # Update Firestore with new suggested products
        user_ref.update({'suggestedProducts': suggested_products})

        return jsonify({'status': 'success', 'updated_user': {'userId': user_id, 'suggestedProducts': suggested_products}})

    return jsonify({'status': 'failed', 'message': 'User is not logged in'}), 403

if __name__ == '__main__':
    app.run(debug=True)
