from flask import Flask, jsonify, request
from flask_cors import CORS
from config import init_mongo, init_jwt_secret, register_user, login_user, token_required
from twitter_scraper import scrape_twitter
from instagram_scraper import scrape_instagram
from linkedin_scraper import scrape_linkedin
import os

app = Flask(__name__)
CORS(app)

# Initialize MongoDB and JWT Secret
mongo = init_mongo(app)
init_jwt_secret(app)

# Testing Route
@app.route('/',methods=['GET'])
def hello():
    return "Hello, World!"

# User Registration Route
@app.route('/register', methods=['POST'])
def register():
    return register_user(mongo)

# User Login Route
@app.route('/login', methods=['POST'])
def login():
    return login_user(mongo, app)

# Token Required Decorator
secure_route = token_required(app, mongo)

# Home Route (Example)
@app.route('/home', methods=['GET'])
@secure_route
def home(current_user):
    return jsonify({"message": "Welcome to the home page!", "user": current_user['username']}), 200

# Scraping Routes (Protected by JWT)
@app.route('/scrape_twitter', methods=['POST'])
@secure_route
def scrape_twitter_route(current_user):
    data = request.json
    return scrape_twitter(data)

@app.route('/scrape_instagram', methods=['POST'])
@secure_route
def scrape_instagram_route(current_user):
    data = request.json
    return scrape_instagram(data)

@app.route('/scrape_linkedin', methods=['POST'])
@secure_route
def scrape_linkedin_route(current_user):
    data = request.json
    result = scrape_linkedin(data)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if no environment variable is set
    app.run(port=port, host='0.0.0.0', debug=True)

# if __name__ == "__main__":
#     app.run(port=5004, host='0.0.0.0',debug=True)
