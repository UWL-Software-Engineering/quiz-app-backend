import unittest
import json
from app import app, client

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.db = client['quizz-application']
        self.users_collection = self.db['users']
        self.users_collection.delete_many({})  # Clear users collection before each test

    def tearDown(self):
        self.users_collection.delete_many({})  # Clear users collection after each test

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

if __name__ == '__main__':
    unittest.main()
