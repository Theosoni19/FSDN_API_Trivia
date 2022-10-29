import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

# Test development 

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('student:student','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
        self.new_question= {"question":"What is the name of United States's president ?",
                            "answer":"Joe Biden",
                            "category":"4",
                            "difficulty":2
                            }

        self.new_question2= {"answer": "Jackson Pollock",
                              "category": 2,
                              "difficulty": 2,
                              "id": 19,
                              "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"}
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["current_category"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=50")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        res = self.client().delete("/questions/15")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==15).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)
        
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/500")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_create_new_question(self):
        res = self.client().post("/question", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_422_if_question_already_exists(self):
        res = self.client().post("/question", json=self.new_question2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "Egyp"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 1)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["current_category"]), 1)

    def test_404_if_getting_question_search_without_results(self):
        res = self.client().post("/books", json={"searchTerm": "highjack"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
    
    def test_422_if_category_does_not_exist(self):
        res = self.client().get("/categories/200/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_get_question_for_quiz(self):
        res = self.client().post("/quizzes", json={"previous_questions":[16,19], 
                                                   "quiz_category": {"type": "Art","id": 2} })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
    
    def test_422_if_randomed_question_is_already_previous_question(self):
        res = self.client().post("/quizzes", json={"previous_questions":[16,17,18,19], 
                                                   "quiz_category": {"type": "Art","id": 2} })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()