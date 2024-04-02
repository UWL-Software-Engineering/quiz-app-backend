from flask import Flask, jsonify, request
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


connection_string = "mongodb://localhost:27017/"

client = MongoClient(connection_string)


db = client['quizz-application']
users_collection = db['users']
questions_collection = db['questions']

app = Flask(__name__)

# Dummy data for the sake of example
quizzes = [
    {
        "id": 1,
        "title": "General Knowledge Quiz",
        "description": "Test your general knowledge with this quiz."
    },
    {
        "id": 2,
        "title": "Science Quiz",
        "description": "A quiz for science enthusiasts."
    }
]

@app.route('/')
def index():
    return "Welcome to the Quiz App!"

@app.route('/quizzes', methods=['GET'])
def get_quizzes():
    return jsonify({"quizzes": quizzes})

@app.route('/quizzes', methods=['POST'])
def add_quiz():
    quiz = request.get_json()
    quizzes.append(quiz)
    return jsonify({"quizzes": quizzes}), 201

# Signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)

    user_data = {
        'username': username,
        'password': hashed_password
    }

    users_collection.insert_one(user_data)

    return jsonify({'message': 'User created successfully'}), 201


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = users_collection.find_one({'username': username})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)
