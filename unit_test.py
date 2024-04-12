import unittest
import json
from app import app, client

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.db = client['quizz-application']
        self.users_collection = self.db['users']
        self.questions_collection = self.db['questions']
        self.leaderboard_collection = self.db['leaderboard']
        self.users_collection.delete_many({})  # Clear users collection before each test

    def tearDown(self):
        self.users_collection.delete_many({})  # Clear users collection after each test
        self.questions_collection.delete_many({})  # Clear questions collection after each test
        self.leaderboard_collection.delete_many({})  # Clear questions collection after each test

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Welcome to the Quiz App!')

    def test_signup_success(self):
        new_user = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.app.post('/signup', json=new_user)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.users_collection.find_one({'username': new_user['username']}))

    def test_signup_failure_duplicate_username(self):
        new_user = {
            "username": "testuser",
            "password": "testpassword"
        }
        # Signup the user first
        self.app.post('/signup', json=new_user)
        # Attempt to signup again with the same username
        response = self.app.post('/signup', json=new_user)
        self.assertEqual(response.status_code, 400)  # Assuming 400 is returned for duplicate username

    def test_login_success(self):
        new_user = {
            "username": "testuser",
            "password": "testpassword"
        }
        self.app.post('/signup', json=new_user)
        response = self.app.post('/login', json=new_user)
        self.assertEqual(response.status_code, 200)

    def test_login_failure_invalid_credentials(self):
        new_user = {
            "username": "testuser",
            "password": "testpassword"
        }
        self.app.post('/signup', json=new_user)
        # Provide incorrect password
        new_user['password'] = 'wrongpassword'
        response = self.app.post('/login', json=new_user)
        self.assertEqual(response.status_code, 401)  # Assuming 401 is returned for invalid credentials

    def test_create_question(self):
        new_question = [
            {"question": "Question 1", "options": ["A", "B", "C", "D"], "correct_answer": "A"},
            {"question": "Question 2", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 3", "options": ["A", "B", "C", "D"], "correct_answer": "A"},
            {"question": "Question 4", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 5", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 6", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 7", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 8", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 9", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 10", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
        ]
        response = self.app.post('/questions', json=new_question)
        self.assertEqual(response.status_code, 201)
        for question in new_question:
            self.assertTrue(self.questions_collection.find_one({'question': question['question']}))

    def test_create_question_failure_duplicate(self):
        new_question = {
            "question": "What is the answer?",
            "options": ["option A", "option B", "option C", "option D"],
            "correct_answer": "option A"
        }
        # Add the same question first
        self.app.post('/questions', json=new_question)
        # Attempt to add the same question again
        response = self.app.post('/questions', json=new_question)
        self.assertEqual(response.status_code, 400)

    def test_get_quizz(self):
        # Add some mock questions to the database
        mock_questions = [
            {"question": "Question 1", "options": ["A", "B", "C", "D"], "correct_answer": "A"},
            {"question": "Question 2", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 3", "options": ["A", "B", "C", "D"], "correct_answer": "A"},
            {"question": "Question 4", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 5", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 6", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 7", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 8", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 9", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
            {"question": "Question 10", "options": ["A", "B", "C", "D"], "correct_answer": "B"},
        ]
        
        response = self.app.post('/questions', json=mock_questions)
        
        # Make a GET request to the endpoint
        response = self.app.get('/get_quizz')
        print(response)
        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains a list of 10 questions
        quizz = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(quizz), 10)
        
        # Check if each question in the quizz does not contain the '_id' field
        for question in quizz:
            self.assertNotIn('_id', question)

        # Clean up: Remove mock questions from the database
        for question in mock_questions:
            self.questions_collection.delete_one(question)
    
    def test_add_score_to_leaderboard(self):
        new_score = {
            "participant_name": "testuser",
            "best_score": 80
        }
        response = self.app.post('/add_leaderboard', json=new_score)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.leaderboard_collection.find_one({'participant_name': new_score['participant_name'], 'best_score': new_score['best_score']}))

    def test_update_score_on_leaderboard(self):
        # Add a score first
        new_score = {
            "participant_name": "testuser",
            "best_score": 80
        }
        self.app.post('/add_leaderboard', json=new_score)

        # Update the score
        updated_score = {
            "participant_name": "testuser",
            "best_score": 90
        }
        response = self.app.post('/add_leaderboard', json=updated_score)
        self.assertEqual(response.status_code, 200)
        updated_entry = self.leaderboard_collection.find_one({'participant_name': new_score['participant_name']})
        self.assertEqual(updated_entry['best_score'], updated_score['best_score'])

    def test_get_leaderboard(self):
        # Add some mock leaderboard entries
        mock_leaderboard_entries = [
            {"participant_name": "user1", "best_score": 80},
            {"participant_name": "user2", "best_score": 85},
            {"participant_name": "user3", "best_score": 70},
            {"participant_name": "user4", "best_score": 90},
            {"participant_name": "user5", "best_score": 95},
        ]
        for entry in mock_leaderboard_entries:
            self.app.post('/add_leaderboard', json=entry)

        # Make a GET request to the leaderboard endpoint
        response = self.app.get('/leaderboard')

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the response contains a list of leaderboard entries
        leaderboard_data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(leaderboard_data['leaderboard']), len(mock_leaderboard_entries))

        # Clean up: Remove mock leaderboard entries from the database
        for entry in mock_leaderboard_entries:
            self.leaderboard_collection.delete_one(entry)

        
if __name__ == '__main__':
    unittest.main()
