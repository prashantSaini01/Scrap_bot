import os
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import jwt
import datetime
from functools import wraps
from bson.objectid import ObjectId

# MongoDB connection setup
def init_mongo(app):
    try:
        # MongoDB Configuration
        mongo_uri = os.getenv('MONGO_URI', "mongodb+srv://14abhay2003:abhay14tyagi@cluster0.cgvg73u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
                # Initialize MongoClient instance
        mongo_client = MongoClient(mongo_uri)
        # Access a specific database (replace 'your_database_name' with the actual name)
        mongo_db = mongo_client.get_database("scraped_data")
          # Check if the connection is successful
        if mongo_client.server_info():  # Raises exception if connection fails
            print("MongoDB connection successful")
        return mongo_db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None  # Return None if connection fails
def init_jwt_secret(app):
    # JWT Secret Key
   app.config['SECRET_KEY'] = os.getenv('JWT_SECRET')

# User Registration
def register_user(mongo_db):

    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not fullname or not email or not username or not password:
        return jsonify({"message": "Fullname, email, username, and password are required!"}), 400

    # Check if the email or username already exists
    if mongo_db.users.find_one({'email': email}):
        return jsonify({"message": "Email already exists!"}), 400
    if mongo_db.users.find_one({'username': username}):
        return jsonify({"message": "Username already exists!"}), 400

    hashed_password = generate_password_hash(password)

    # Insert the user into the MongoDB collection
    mongo_db.users.insert_one({
        'fullname': fullname,
        'email': email,
        'username': username,
        'password': hashed_password
    })

    return jsonify({"message": "User registered successfully!"}), 201
# Login function
def login_user(mongo_db, app):

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required!"}), 400

    # Check if the user exists by username
    user = mongo_db.users.find_one({'username': username})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({"message": "Invalid credentials!"}), 401

    # Generate JWT token valid for 30 minutes
    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expires in 30 minutes  # Token expires in 30 minutes
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token}), 200

# Token Required decorator
def token_required(app, mongo_db):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('x-access-token')

            if not token:
                return jsonify({"message": "Token is missing!"}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id = ObjectId(data['user_id'])
                current_user = mongo_db.users.find_one({'_id': user_id})
                if not current_user:
                    return jsonify({"message": "User not found!"}), 404
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired!"}), 401
            except Exception as e:
                return jsonify({"message": f"Token is invalid! {str(e)}"}), 401

            return f(current_user, *args, **kwargs)

        return decorated
    return wrapper
