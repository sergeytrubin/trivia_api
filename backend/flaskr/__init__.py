import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Page size
QUESTIONS_PER_PAGE = 10


# Helper to paginate the questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={"/": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS'
        )
        return response

    ##############################################
    ###             Endpoints                  ###
    ##############################################

    # Test: curl -i http://127.0.0.1:5000/categories
    @app.route('/categories')
    def get_categories():
        """"Get request to retrieve all categories"""

        # Retrieve all categories
        selection = Category.query.all()

        # Add categories to dictionary
        categories = {category.id: category.type for category in selection}

        # Abort with 404 if no results found
        if len(categories) == 0:
            abort(404)

        # Return data in JSON format
        return jsonify({
            "success": True,
            "categories": categories,
            "total_categories": len(selection)
        })

    #Test: curl -i http://127.0.0.1:5000/questions?page=1
    @app.route('/questions')
    def get_paginated_questions():
        """Get request to retrieve all questions"""

        # Retrive questions and paginate
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        # Abort with 404 if no questions retrieved
        if len(current_questions) == 0:
            abort(404)

        # Retrieve and add categories to dictionary
        categories = {
            category.id: category.type for category in Category.query.all()}

        # Return data in JSON format
        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(selection),
            "categories": categories
        })

    # Test delete question: curl -X DELETE http://127.0.0.1:5000/questions/8
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Delete request to delete question by id"""

        try:
            # Retrieve a question by id
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            # Abort 404 if result is None
            if question is None:
                abort(404)

            # Delete the question
            question.delete()

            # Retrieve paginated questions for return message
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            # Return data in JSON format
            return jsonify({
                "success": True,
                "deleted": question_id,
                "total_questions": len(selection)
            })

        except:
            # Abort 422 if delete could not be processed
            abort(422)


    # Test create new question
    # curl -X POST -H "Content-Type: application/json" -d
    # '{"question": "Who came up with the three laws of motion?",
    # "answer": "Sir Isaac Newton", "category": 4, "difficulty": 1}'
    # http://127.0.0.1:5000/questions
    @app.route('/questions', methods=['POST'])
    def add_question():
        """Post request to create new question"""

        # Get the new question data from the form
        body = request.get_json()

        #Format new question
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        try:
            # POST the new question to database
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            # Retrieve paginated questions for return message
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "created": question.id,
                "questions": current_questions,
                "total_questions": len(selection)
            })

        except:
            abort(422)

    # curl -X POST -H "Content-Type: application/json" -d
    # '{"searchTerm": "title"}' http://127.0.0.1:5000/questions/search
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """Post request to find all questions based on a search term"""

        # Collect data from the form
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        # Retrive data filtered by search term
        if search_term is not None:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            current_questions = paginate_questions(request, selection)


            # Abort 404 if result is empty
            if len(current_questions)== 0:
                abort(404)

            # Return data in JSON format
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_found_questions": len(selection)
            })


    # curl -i http://127.0.0.1:5000/categories/1/questions
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        """Get all questions in category"""

        # Retrieve category by id
        category = Category.query.filter(
                Category.id == category_id).one_or_none()

        # Abort 400 if result is None
        if category is None:
            abort(400)

        # Retrieve paginated questions for return message
        selection = Question.query.filter(
            Question.category == category.id).all()
        current_questions = paginate_questions(request, selection)

        # Abort 404 if result is empty
        if len(selection) == 0:
            abort(404)

        # Return data in JSON format
        return jsonify({
            "success": True,
            "current_category": category.type,
            "questions": current_questions,
            "total_questions_by_category": len(selection)
        })

    #curl -X POST -H "Content-Type: application/json" -d
    # '{"previous_questions": [],
    # "quiz_category": {"type": "Science", "id": 1}}'
    # http://127.0.0.1:5000/quizzes
    @app.route('/quizzes', methods=['POST'])
    def play_trivia_quiz():
        """Create a post request to retrieve questions for the game"""

        # Collect data from the form
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        try:
            # Retrieve question that were not asked per chosen category
            if quiz_category['id'] == 0:
                selection = Question.query.filter(
                        Question.id.notin_((previous_questions))).all()
                total_questions = Question.query.all()
            else:
                selection = Question.query.filter(
                    Question.category==quiz_category['id']).filter(
                        Question.id.notin_((previous_questions))).all()
                total_questions = Question.query.filter(
                    Question.category==quiz_category['id']).all()

            # Stop the game if no questions in category left
            if len(previous_questions) == len(total_questions):
                return jsonify({
                    "success": True,
                    "question": None
                })

            # Retrieve new random question fron the selection
            new_question = selection[random.randrange(0, len(selection))]

            # Return new question
            return jsonify({
                "success": True,
                "question": new_question.format()
            })
        except:
            abort(422)



    ##############################################
    ###             Error handlers             ###
    ##############################################

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405


    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        }), 500

    return app

