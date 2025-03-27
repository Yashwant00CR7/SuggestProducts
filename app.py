# from flask import Flask, jsonify, request
# import firebase_admin
# from firebase_admin import credentials, firestore

# app = Flask(__name__)

# # Initialize Firebase
# cred = credentials.Certificate('firebase_config.json')
# firebase_admin.initialize_app(cred)

# # Initialize Firestore DB
# db = firestore.client()

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

@app.route('/')
def home():
    return "Firebase Connected with Flask!"

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    doc_ref = db.collection('users').add(data)
    return jsonify({"status": "success", "id": str(doc_ref[1].id)})

@app.route('/update_suggestions', methods=['POST'])
def update_suggestions():
    data = request.json
    user_id = data.get('userId')

    if not user_id:
        return jsonify({"status": "failed", "message": "User ID is required"}), 400

    # Get user document by userId
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify({"status": "failed", "message": "User not found"}), 404

    user_data = user_doc.to_dict()

    # Check if the user is logged in
    if user_data.get("loggedIn"):
        username = user_data.get("name", "Unknown User")

        # Update suggestedProducts with the username
        user_ref.update({"suggestedProducts": [username,user_id]})

        return jsonify({"status": "success", "message": "Suggested products updated", "updated_user": username})
    else:
        return jsonify({"status": "failed", "message": "User is not logged in"}), 403

if __name__ == '__main__':
    if __name__ == "__main__":
      from os import environ
      app.run(host="0.0.0.0", port=environ.get("PORT", 5000))

