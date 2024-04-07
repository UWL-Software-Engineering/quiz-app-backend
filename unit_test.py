import unittest
import json
from app import app, client

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.db = client['quizz-application']
        self.users_collection = self.db['users']
        self.questions_collection = self.db['questions']
        self.users_collection.delete_many({})  # Clear users collection before each test

    def tearDown(self):
        self.users_collection.delete_many({})  # Clear users collection after each test
        self.questions_collection.delete_many({})  # Clear questions collection after each test

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
        new_question = {
            "question": "What is the answer?",
            "options": ["option A", "option B", "option C", "option D"],
            "correct_answer": "option A"
        }
        response = self.app.post('/questions', json=new_question)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.questions_collection.find_one({'question': new_question['question']}))

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
if __name__ == '__main__':
    unittest.main()
