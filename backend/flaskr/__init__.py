import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  def format_categories(formatted_cats):
    cat_obj = {}
    for cat in formatted_cats:
      cat_obj[cat["id"]] = cat["type"]
    return cat_obj

  @app.route('/categories', methods=['GET'])
  def get_cats():
    try: 
      unformatted_cats = Category.query.all()
      total_cats = len(unformatted_cats)
      if(total_cats == 0):
        abort(404)
      formatted_cats = [cat.format() for cat in unformatted_cats]
      cat_obj = format_categories(formatted_cats)
      return jsonify({
        "success": True,
        "categories": cat_obj,
        "total_cats": total_cats
      }), 200
    except:
      abort(422)

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
  def pagination(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    return questions[start:end]
  
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try: 
      selection = Question.query.all()
      questions = pagination(request, selection)
      if(len(questions) == 0):
        abort(404)
      unformatted_cats = Category.query.all()
      formatted_cats = [cat.format() for cat in unformatted_cats]
      cat_obj = format_categories(formatted_cats)
      current_cat = 0
      total_questions = len(Question.query.all())

      return jsonify({
        "success": True,
        "questions": questions,
        "total_questions": total_questions,
        "categories": cat_obj,
        "current_category": current_cat
      }), 200
    except:
      abort(404)
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:id>", methods=["DELETE"])
  def delete_question(id):
    question = None
    try:
      question = Question.query.filter(Question.id == id).one_or_none()
    except:
      abort(422)
    if question == None:
      abort(404)
    else:
      try:
        question.delete()
        return jsonify({
          "success": True,
          "deleted": id
        }), 200
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
  @app.route('/questions', methods=["POST"])
  def post_question():
    request_data = request.get_json()
    question = request_data.get("question", None)
    answer = request_data.get("answer", None)
    category = request_data.get("category", None)
    difficulty = request_data.get("difficulty", None)
    if (question is None) or (answer is None) or(category is None) or (difficulty is None):
      abort(400)
    else:
      new_question = Question(question=question, answer=answer, category=category, difficulty=int(difficulty))
      print(new_question)
      try:
        new_question.insert()
      except:
        abort(422)
      return jsonify({
        "success": True,
        "created": new_question.id
      }), 200


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions/search", methods=["POST"])
  def question_search():
    data = request.get_json()
    search_term = data.get("searchTerm", None)
    if(search_term == None):
      abort(400)
    else:
      questions = None
      total_questions = None
      try:
        questions = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()
      except:
        abort(422)
      try:
        total_questions = len(Question.query.all())
      except:
        abort(422)
      formatted_questions = [question.format() for question in questions]
      return jsonify({
        "success": True,
        "questions": formatted_questions,
        "total_questions": total_questions,
        "search_count": len(formatted_questions),
        "current_category": 0
      }), 200
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:id>/questions", methods=["GET"])
  def get_cat_questions(id):
    cat = None
    try:
      cat = Category.query.filter(Category.id == id).one_or_none()
    except:
      abort(422)
    if cat == None:
      abort(404)
    else:
      total_questions = None
      try:
        total_questions = len(Question.query.all())
      except:
        abort(422)
      formatted_questions = pagination(request, cat.questions)
      return jsonify({
        "success": True,
        "questions": formatted_questions,
        "num_cat_questions": len(formatted_questions),
        "total_questions": total_questions,
        "current_category": id
      }), 200
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
  @app.route('/quizzes', methods=["POST"])
  def get_next_question():
    request_data = request.get_json()
    previous_questions = request_data.get("previous_questions", None)
    question_category = request_data.get("quiz_category", None)
    if (previous_questions == None) or (question_category == None):
      abort(400)
    if question_category["id"] == 0:
      questions = None
      try:
        questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
      except:
        abort(422)
      if questions == None:
        abort(404)
      else:
        next_question = random.choice(questions).format()
        return jsonify({
              "success": True,
              "question": next_question
            }), 200

    if (previous_questions == None) or (question_category == None):
      abort(400)
    else:
      cat = None
      try:
        cat = Category.query.filter(Category.id == int(question_category["id"])).one_or_none()
      except:
        abort(422)
      if cat == None:
        abort(404)
      else:
        cat_questions = cat.questions
        if len(cat_questions) == 0:
          abort(404)
        else:
          next_question = None
          potential_questions = Question.query.filter((Question.category == question_category["id"]) & (~Question.id.in_(previous_questions))).all()
          if len(potential_questions) == 0:
            abort(404)
          next_question = random.choice(potential_questions).format()
          if next_question == None:
            abort(404)
          else: 
            return jsonify({
              "success": True,
              "question": next_question
            }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "not found"
    }), 404    
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method Not Allowed"
    }), 405
  @app.errorhandler(400)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad Request"
    }), 400
  return app

    