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

    def test_signup(self):
        new_user = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.app.post('/signup', json=new_user)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.users_collection.find_one({'username': new_user['username']}))

    def test_login(self):
        new_user = {
            "username": "testuser",
            "password": "testpassword"
        }
        self.app.post('/signup', json=new_user)
        response = self.app.post('/login', json=new_user)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
