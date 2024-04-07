from flask import Flask, jsonify, request
from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# connection_string = "mongodb+srv://UWLStudent:UWL123@cluster0.xzxhbrp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# client = MongoClient(connection_string)

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")
username = os.environ.get("MONGODB_USERNAME")
cluster_uri = os.environ.get("CLUSTER_URI")
uri = f"mongodb+srv://{username}:{password}@{cluster_uri}/"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


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


# Question endpoint
@app.route("/questions", methods=["POST"])
def create_question():
    data = request.get_json()
    if not isinstance(data, list):
        data = [data]

    for question_data in data:
        question = question_data.get("question")
        options = question_data.get("options")
        correct_answer = question_data.get("correct_answer")

        if not question or not correct_answer or not options:
            return jsonify({"error": "Question, options, and correct_answer are required"}), 400

        if questions_collection.find_one({"question": question}):
            return jsonify({'error': 'Question already exists'}), 400

        question_data = {
            'question': question,
            'options': options,
            'correct_answer': correct_answer
        }

        questions_collection.insert_one(question_data)

    return jsonify({'message': 'Questions created successfully'}), 201

# Get questions endpoint
@app.route("/get_quizz", methods=["GET"])
def get_quizz():
    # Fetch all questions from the database
    all_questions = list(questions_collection.find())
    
    # Check if there are at least 10 questions in the database
    if len(all_questions) < 10:
        return jsonify({"error": "There are not enough questions in the database"}), 400

    # Select 10 random questions
    random_questions = random.sample(all_questions, 10)
    
    # Remove the MongoDB ObjectId from each question
    for question in random_questions:
        question.pop('_id', None)
    
    return jsonify(random_questions), 200


if __name__ == '__main__':
    app.run(debug=True)
