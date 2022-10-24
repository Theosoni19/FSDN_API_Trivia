import os
import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, setup_db

QUESTIONS_PER_PAGE = 10

    # Ranging questions by 10 before sending to frontend
    
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

     # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
  
    
    # handle GET requests for all available categories.

    @app.route("/categories")
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {}

        for category in categories:
            formatted_categories[category.id]= category.type
            
        return jsonify({
            "success": True,
            "categories": formatted_categories
        })


        
    # handling GET requests for questions,including pagination (every 10 questions).
  
    @app.route("/questions")
    def get_questions():
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = Category.query.order_by(Category.id).all()
            formatted_categories = {}

            for category in categories:
                formatted_categories[category.id]= category.type
            
            data = [ Category.query.get(question.category).type for question in selection ]
            data = list(dict.fromkeys(data))

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                    "categories": formatted_categories,
                    "current_category": data
                }
            )



    # Deleting question using a question ID.
    
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True
                }
            )

        except:
            abort(422)


    # Creating a new question

    @app.route("/question", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        

        try:
            if Question.query.filter(Question.question==new_question).one_or_none() is not None:
                abort(400)

            question = Question(question=new_question, 
                                answer=new_answer, 
                                category=new_category, 
                                difficulty= new_difficulty)
            
            question.insert()

            return jsonify({
                            "success":True
                            })
        except:
            abort(422)


  
    # Handling request to get questions based on a search term.
    
    @app.route("/questions", methods=["POST"])
    def search_questions():
        body = request.get_json()
        searchTerm = body.get("searchTerm", None)

        try:
            questions = Question.query.filter(Question.question.ilike('%'+ searchTerm +'%')).all()
            data = [ Category.query.get(questionData.category).type for questionData in questions ]
            data = list(dict.fromkeys(data))
            formatted_questions = [ question.format() for question in questions]
            
            return jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": data
                }
            )

        except:
            abort(422)

    

    # Handling request to get questions based on category.

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(Question.category == category_id).all()
            data = Category.query.filter(Category.id==category_id).first()
            formatted_questions = [ question.format() for question in questions]

            if questions is None:
                abort(404)

            return jsonify(
                {   
                    "success":True,
                    "questions": formatted_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": data.type
                }
            )

        except:
            abort(422)



    # Handling request to get questions to play the quiz.

    @app.route("/quizzes", methods=["POST"])
    def get_question_for_quiz():
        body = request.get_json()

        previousQuestions = body.get("previous_questions", None)
        quizCategory = body.get("quiz_category", None)
        try:
            questions = Question.query.filter(Question.category==quizCategory["id"]).all()
            formatted_questions = [ question.format() for question in questions if question.id not in previousQuestions]
            
            if formatted_questions is None:
                abort(400)
            else:
                currentQuestion= random.choice(formatted_questions)

            return jsonify(
                {
                    "success": True,
                    "question": currentQuestion
                }
            )

        except:
            abort(422)



   #  Creating error handlers for all expected errors

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )


    return app

