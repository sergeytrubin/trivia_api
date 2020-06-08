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
    #CORS(app, resources={r"/questions/*": {"origins": "*"}})
    CORS(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    ##############################################
    ###             Endpoints                  ###
    ##############################################
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    # curl -i http://127.0.0.1:5000/categories
    @app.route('/categories')
    def get_categories():
        selection = Category.query.order_by(Category.id).all()
        categories = [category.format() for category in selection]

        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": categories,
            "total_categories": len(Category.query.all())
        })


    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    # Success: curl -i http://127.0.0.1:5000/questions?page=1
    # Test 404: curl -i http://127.0.0.1:5000/questions?page=1000
    @app.route('/questions')
    def get_paginated_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(Question.query.all())
        })


    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    # Delete question: curl -X DELETE http://127.0.0.1:5000/questions/8
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            
            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "deleted": question_id,
                "total_questions": len(Question.query.all())
            })
        
        except:
            abort(422)


    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    # Create new question
    # curl -X POST -H "Content-Type: application/json" -d 
    # '{"question": "Who came up with the three laws of motion?", 
    # "answer": "Sir Isaac Newton", "category": 4, "difficulty": 1}' 
    # http://127.0.0.1:5000/questions
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty 
            )
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "created": question.id,
                "questions": current_questions,
                "total_questions": len(Question.query.all())
            })
        
        except:
            abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    # curl -X POST -H "Content-Type: application/json" -d 
    # '{"searchTerm": "title"}' http://127.0.0.1:5000/questions/search
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """Find all questions based on a search term"""
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term is not None:
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions)== 0:
                abort(404)

            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_found_questions": len(selection)
            })


    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    # curl -i http://127.0.0.1:5000/categories/1/questions
    @app.route('/categories/<int:id>/questions')
    def retrieve_questions_by_category(id):
        category = Category.query.filter(
                Category.id == id).one_or_none()     
            
        if category is None:
            abort(400)

        try:
            selection = Question.query.filter(
                Question.category == category.id).all()

            if len(selection) == 0:
                abort(404)
            
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                'current_category': category.type,
                "questions": current_questions,
                "total_questions_by_category": len(selection)
            })
        
        except:
            abort(422)


    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

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

    