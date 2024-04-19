from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from logger_config import Logger
from elasticapm.contrib.flask import ElasticAPM

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
leaderboard_collection = db['leaderboard']

app = Flask(__name__)
CORS(app)

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

apm = ElasticAPM(app, server_url='http://0.0.0.0:8200', service_name="Quiz-Application", logging=False)
logger = Logger.get_logger()
logger.info("APM connected!")

@app.route('/')
def index():
    logger.info("APM connected!")
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

# Leaderboard endpoint
@app.route("/add_leaderboard", methods=["POST"])
def create_leaderboard():
    data = request.get_json()
    participant_name = data.get('participant_name')
    best_score = data.get('best_score')

    if not participant_name or not best_score:
        return jsonify({'error': 'Participant name and Best score are required'}), 400

    if leaderboard_collection.find_one({'participant_name': participant_name}):
        query = {'participant_name': participant_name}
        update = {'$set': {'best_score': best_score}}
        leaderboard_collection.update_one(query, update)
        return jsonify({'message': 'Score updated on leaderboard successfully'}), 200

    leaderboard_data = {
        'participant_name': participant_name,
        'best_score': best_score
    }

    leaderboard_collection.insert_one(leaderboard_data)

    return jsonify({'message': 'Leaderboard data created successfully'}), 200

# Retrieve leaderboard data
@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard_data = list(leaderboard_collection.find({}, {'_id': 0}))
    return jsonify({'leaderboard': leaderboard_data}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

