import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.user = 'dbuser'
        self.password = 'zubur1'
        self.database_name = "trivia_test"
        self.database_path = f"postgresql://{self.user}:{self.password}@{'localhost:5432'}/{self.database_name}"
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who came up with the three laws of motion?',
            'answer': 'Sir Isaac Newton',
            'difficulty': 1,
            'category': 4
        }

        self.quiz_test = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        """Test: Retrieve all categories"""
        # Variables
        res = self.client().get('/categories')
        data = json.loads(res.data)
        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))  
   
    def test_get_paginated_questions(self):
        """Test: Retrieve paginated questions"""
        # Variables
        res = self.client().get('/questions')
        data = json.loads(res.data)

        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    def test_404_sent_requesting_beyond_valid_page(self):
        """Test: 404 error when the resource does not exists"""
        # Variables
        res = self.client().get(
            '/questions?page=1000', json={'difficulty': 1})
        data = json.loads(res.data)

        # Tests
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    def test_delete_question(self):
        """Test: Delete a question. Runs only the first time"""
        # Variables
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 2).one_or_none()

        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        """Test: 422 eror when the question is not exist"""
        # Variables
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        # Tests
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_create_question(self):
        """Test: Create new question"""
        # Variables
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_405_if_question_creation_not_alllowed(self):
        """Test: 405 error of question creation with incorrect endpoint"""
        # Variables
        res = self.client().post('/questions/405', json=self.new_question)
        data = json.loads(res.data)
        
        # Tests
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')

    def test_search_questions_by_given_search_term(self):
        """Test: Search questions by given search term"""
        # Variables
        res = self.client().post(
            '/questions/search', json={"searchTerm": "title"})
        data = json.loads(res.data)
        
        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_found_questions'])

    def test_404_error_search_questions_by_given_search_term(self):
        """Test: No resluts when search questions by given search term"""
        # Variables
        res = self.client().post(
            '/questions/search', json={"searchTerm": "blabla"})
        data = json.loads(res.data)
        
        # Tests
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_retrieve_questions_by_category(self):
        """Test: Retrieve questions by category"""
        # Variables
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions_by_category'])

    def test_bad_category_retrieve_questions_by_category(self):
        """Test: Faled to questions by category - wrong category ID"""
        # Variables
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        # Tests
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    def test_play_trivia_quiz(self):
        """Test: Play the quiz with test quiz data"""
        # Variables
        res = self.client().post('/quizzes', json=self.quiz_test)
        data = json.loads(res.data)
        
        # Tests
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 1)

    def test_422_error_play_trivia_quiz(self):
        """Test: 422 error if the data is empty"""
        # Variables
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        # Tests
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()