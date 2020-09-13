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
        self.client = self.app.test_client()
        self.new_question = {
            "question": "What field IBM Watson supports?",
            "answer": "Artificial intelligence",
            "category": 1,
            "difficulty": 10
        }
        self.new_wrong_question = {
            "question": "What field IBM Watson supports?",
            "category": 1,
            "difficulty": 10
        }
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Selimzohnyel5asa','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
        res = self.client.get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        cat_num = len(Category.query.all())
        self.assertEqual(data["total_cats"], cat_num)
    
    def test_get_cats_err(self):
        res = self.client.get('/cats')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "not found")
    
    def test_get_questions(self):
        res = self.client.get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        total_questions = len(Question.query.all())
        self.assertEqual(data["total_questions"], total_questions)
        self.assertLessEqual(len(data["questions"]), 10)
        self.assertEqual(data["current_category"], 0)
    
    def test_get_questions_err(self):
        res = self.client.get('/questions?page=1000')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "not found")

    def test_delete_question(self):
        res = self.client.delete('/questions/19')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 19)
        question = Question.query.filter(Question.id == 19).one_or_none()
        self.assertEqual(question, None)
    
    def test_delete_question_error(self):
        res = self.client.delete("/questions/1000")
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "not found")
    
    def test_post_question(self):
        res = self.client.post("/questions", json=self.new_question, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        created_id = data["created"]
        question = Question.query.filter(Question.id == created_id).one_or_none()
        self.assertNotEqual(question, None)
        self.assertEqual(question.question, self.new_question["question"])
        self.assertEqual(question.answer, self.new_question["answer"])
        self.assertEqual(question.category, self.new_question["category"])
        self.assertEqual(question.difficulty, self.new_question["difficulty"])
    
    def test_post_question_err(self):
        res = self.client.post("/questions", json=self.new_wrong_question, content_type="application/json")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")
    
    def test_question_search(self):
        res = self.client.post("/questions/search", json={"searchTerm": "IBM"}, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        total_questions = len(Question.query.all())
        self.assertEqual(data["total_questions"], total_questions)
        num_search_res = len(Question.query.filter(Question.question.ilike("%{}%".format("IBM"))).all())
        self.assertEqual(num_search_res, len(data["questions"]))
        self.assertEqual(num_search_res, data["search_count"])
    
    def test_question_search_err(self):
        res = self.client.post("/questions/search", json={"search": "IBM"}, content_type="application/json")
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")
    
    def test_get_cat_questions(self):
        res = self.client.get("/categories/1/questions")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        cat = Category.query.filter(Category.id == 1).one_or_none()
        num_cat_questions = len(cat.questions)
        self.assertEqual(data["num_cat_questions"], num_cat_questions)
        self.assertEqual(len(data["questions"]), num_cat_questions)
        total_questions = len(Question.query.all())
        self.assertEqual(data["total_questions"], total_questions)
    
    def test_get_cat_questions_err(self):
        res = self.client.get("/categories/100/questions")
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "not found")
    
    def test_quizzes(self):
        res = self.client.post('/quizzes', json={"previous_questions": [5, 9, 4], "quiz_category": {"type": "Science", "id": 1}}, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], 1)
    
    def test_quiz_err(self):
        res = self.client.post('/quizzes', json={"previous_questions": [5, 9, 4]})
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")
    







# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()