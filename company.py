from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
import bcrypt
from bson.objectid import ObjectId

app = Flask(__name__)

# Secret key for signing JWT
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Replace with a strong secret key
jwt = JWTManager(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/SysandSur")
db = client.SysandSur  # Database name

# Collection references
companies = db.company
users = db.Users

### COMPANY ENDPOINTS ###

# Company Signup
@app.route('/company/signup', methods=['POST'])
def company_signup():
    data = request.json
    if not data or "name" not in data or "password" not in data:
        return jsonify({"error": "Invalid input"}), 400

    company_name = data['name']
    password = data['password']

    # Check if the company already exists
    if companies.find_one({"name": company_name}):
        return jsonify({"error": "Company already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Store the company data in the database
    company_id = companies.insert_one({
        "name": company_name,
        "password": hashed_password,
        "users": []  # Initialize an empty array to store user IDs
    }).inserted_id

    return jsonify({"message": "Company registered successfully", "company_id": str(company_id)}), 201


# Company Login
@app.route('/company/login', methods=['POST'])
def company_login():
    data = request.json
    if not data or "name" not in data or "password" not in data:
        return jsonify({"error": "Invalid input"}), 400

    company_name = data['name']
    password = data['password']

    # Authenticate company
    company = companies.find_one({"name": company_name})
    if not company or not bcrypt.checkpw(password.encode('utf-8'), company['password']):
        return jsonify({"error": "Invalid company name or password"}), 401

    # Generate access token for the company
    access_token = create_access_token(identity=str(company["_id"]))  # Use company ID as string identity
    return jsonify(access_token=access_token), 200


### USER MANAGEMENT ENDPOINTS ###

# Add User (by Company)
@app.route('/company/add_user', methods=['POST'])
@jwt_required()  # Requires the company to be authenticated
def add_user():
    current_company_id = get_jwt_identity()  # Extract company_id as string

    user_data = request.json
    name = user_data.get("name")
    face_encodings = user_data.get("face_encodings")

    # Validate input
    if not name or not face_encodings or not isinstance(face_encodings, list):
        return jsonify({"error": "Invalid input: 'name' and 'face_encodings' (array) are required"}), 400

    # Add user to the user collection
    user = {"name": name, "face_encodings": face_encodings, "company_id": current_company_id}
    user_id = users.insert_one(user).inserted_id

    # Update the company's document to include this user's ID
    companies.update_one(
        {"_id": ObjectId(current_company_id)},
        {"$push": {"users": user_id}}
    )

    return jsonify({"message": f"User {name} added successfully.", "user_id": str(user_id)}), 201


# Get All Users for the Logged-in Company
@app.route('/company/users', methods=['GET'])
@jwt_required()
def get_users():
    current_company_id = get_jwt_identity()  # Extract company_id as string

    # Fetch the company and its users
    company = companies.find_one({"_id": ObjectId(current_company_id)}, {"users": 1})
    if not company or "users" not in company:
        return jsonify({"error": "No users found for this company"}), 404

    # Fetch user details for all user IDs in the company's "users" array
    company_users = list(users.find({"_id": {"$in": company["users"]}}, {"_id": 1, "name": 1, "face_encodings": 1}))
    for user in company_users:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string for JSON serialization

    return jsonify(company_users), 200


# Get a Specific User's Details
@app.route('/company/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_company_id = get_jwt_identity()  # Extract company_id as string

    # Validate user_id
    if not ObjectId.is_valid(user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    # Fetch user by ID and ensure they belong to the authenticated company
    user = users.find_one(
        {"_id": ObjectId(user_id), "company_id": current_company_id},
        {"_id": 1, "name": 1, "face_encodings": 1}
    )
    if not user:
        return jsonify({"error": "User not found or does not belong to your company"}), 404

    user["_id"] = str(user["_id"])  # Convert ObjectId to string for JSON serialization
    return jsonify(user), 200


if __name__ == '__main__':
    app.run(debug=True)
