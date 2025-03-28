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

# Product recommendations based on user roles
role_based_recommendations = {
    "Foodie": ["Chocolate", "Noodles", "Biscuit"],
    "Techie": ["Watches", "Shampoo", "Coca-Cola"],
    "Sports": ["Bisleri", "Chocolate", "Coca-Cola"],
    "Business": ["Watches", "Bisleri", "Harpic"],
    "Education": ["Biscuit", "Noodles", "Chocolate"],
    "Homemaker": ["Harpic", "Shampoo", "Biscuit"]
}

@app.route('/')
def home():
    return "Firebase Connected with Flask!"

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
    if user_data.get('loggedIn', True):
        user_role = user_data.get('role', 'Unknown')

        # Get suggested product names based on the role
        suggested_product_names = role_based_recommendations.get(user_role, [])

        # Retrieve corresponding Firestore document UIDs
        suggested_product_uids = []
        products_ref = db.collection('products')

        for product_name in suggested_product_names:
            query = products_ref.where("ProductName", "==", product_name).stream()
            for product in query:
                suggested_product_uids.append(product.id)  # Getting the Firestore document UID

        # Update Firestore with new suggested product UIDs
        user_ref.update({'suggestedProducts': suggested_product_uids})

        return jsonify({'status': 'success', 'updated_user': {'userId': user_id, 'suggestedProducts': suggested_product_uids}})

    return jsonify({'status': 'failed', 'message': 'User is not logged in'}), 403

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=environ.get("PORT", 5000))
