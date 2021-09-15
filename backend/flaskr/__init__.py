import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category



# def paginate_questions(request, selection):
#   page = request.args.get('page', 1, type=int)
#   start =  (page - 1) * QUESTIONS_PER_PAGE
#   end = start + QUESTIONS_PER_PAGE

#   question = [question.format() for question in selection]
#   current_question = question[start:end]

#   return current_question

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)   
  CORS(app)
## SEMDING HEADERS ####################################################
  @app.after_request
  def after_request(response):

    response.headers.add('Access-Conrool-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add('Access-Conrool-Allow-Methods','PAST, PUT, PATCH, GET, OPTION')

    return response

  # endpoinds

## GETTING CATEGORIES #################################################
  @app.route('/categories', methods=['GET'])
  def get_categories_data():

    try:
      # geting data from db 
      categories = Category.query.order_by(Category.id).all()
      category = {}

      # if data is not found
      if not categories:
        abort(404)

      # formating data idk i didnt find easy way for it
      for formated_category in categories:
        category.update({
          formated_category.id : formated_category.type, 
          }) 

      # returning data as usual to client 
      return jsonify({
        'success': True,
        'categories': category
        })

    except:
      abort(422)

## geting questions ##################################################
  @app.route('/questions', methods=['GET'])
  def get_questions_data():

    if True:
      # geting data from database
      items_limit = request.args.get('limit', 10, type=int)
      selected_page = request.args.get('page', 1, type=int)
      current_index = selected_page - 1
      questions = Question.query.order_by(Question.id).limit(items_limit).offset(current_index * items_limit).all()
      current_questions = [question.format() for question in questions]

      
      if len(current_questions) == 0:
        abort(404)

      categories = Category.query.order_by(Category.id).all()
      category = {}

      for formated_category in categories:
        category.update({
          formated_category.id : formated_category.type, 
          }) 

      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(questions),
        'categories': category,
        'currentCategory': category[current_questions[0]['category']]
       })

    else:
      abort(422)

## GET EXACT CATEGORIES ##############################################
  @app.route('/categories/<int:category_id>/questions', methods = ["GET"])
  def get_questions_by_catego(category_id):
    if True:
      items_limit = request.args.get('limit', 10, type=int)
      selected_page = request.args.get('page', 1, type=int)
      current_index = selected_page - 1

      # GETING datas from database
      questions_total = Question.query.order_by(Question.id).all()
      questions = Question.query.order_by(Question.id).filter(Question.category==category_id).limit(items_limit).offset(current_index * items_limit).all()
      current_questions = [question.format() for question in questions]
      if not questions:
        abort(404)


      categories = Category.query.order_by(Category.id).all()

      category = {}
      for formated_category in categories:
        category.update({
          formated_category.id : formated_category.type, 
          }) 

      # if there are no data in db return Not Found Error
      if len(current_questions) == 0 or not categories:
        abort(404)

      # returning data to client
      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions':len(questions_total),
        'categories':category,
        'currentCategory':category[category_id]
        })

    # IF THERE PROBEM WITH, RETURNING SERVER ERROR
    else:
      abort(422)

## POST QUIZZ WITH CATEGORY ###########################################
  @app.route('/quizzes', methods=['POST'])
  def new_unique_quizz():
    try:
      body = request.get_json()

      previous_questions=body.get("previous_questions", None)
      quiz_category=body.get("quiz_category")
      # print('quizzes->', quiz_category)

      category_id = quiz_category['id']


      if previous_questions is None:
        abort(422)
      """-----------------------------------------------------------------""" 
      # i saw notin_ method in stackocerflow that is interesting for me
      if quiz_category['id'] == 0:
        all_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()

      else:
        all_questions = Question.query.filter(Question.id.notin_(previous_questions)).filter(Question.category == category_id).all()

      if all_questions:
        random_num = random.randint(0, len(all_questions)-1)
        # print('random_num', random_num)
        new_quizz = all_questions[random_num]

###### RETURNING DATA to CLIENT #################################################
        return jsonify({
          'success': True,
          'question': new_quizz.format()
          })
      else:
        abort(404)

    except:
      abort(422)



## DELETE QUESIONS HANDLER ############################################
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_quesion_by_id(question_id):

    try:
      # GETUNG DATA FROM DATABASE
      question = Question.query.filter(Question.id==question_id).one_or_none()

      # IF GETING DATA FINISHED SUCCESSFULLY THEN 'DELETE' FORM DATAS
      question.delete()

      return jsonify({
        'success': True,
        'deleted_id': question_id
        })


    # IF THERE IS ERROR RETURN 'BAD REQUEST' ERROR
    except:
      abort(400)

## POST NEW QUESTION HANDLER ###########################################
  @app.route('/questions', methods=['POST'])
  def create_question():

    # GETTING JSON BODY FROM CLIENT 
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    search = body.get('searchTerm', None)

    # FILTER CATIGORIES AND TOTAL NUMBER OF QUESTIONS
    questions_total = Question.query.order_by(Question.id).all()
    category = {}

    categories = Category.query.order_by(Category.id).all()
    for formated_category in categories:
      category.update({
        formated_category.id : formated_category.type, 
        })
#
    try:
      if search:
        items_limit = request.args.get('limit', 10, type=int)
        selected_page = request.args.get('page', 1, type=int)
        current_index = selected_page - 1
        questions = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search))).limit(items_limit).offset(current_index * items_limit).all()
        current_questions = [question.format() for question in questions]
        return jsonify({
          'success': True,
          'questions': current_questions,
          'totalQuestions': len(questions_total),
          'currentCategory': category[current_questions[0]['category']] })

      else:
        question = Question(
          question=new_question, 
          answer=new_answer, 
          difficulty=new_difficulty,
          category=new_category,
          )
        question.insert()

        questions = Question.query.order_by(Question.id).all()

        return jsonify({
          'success': True,
          'created': question.id,
          'totalQuestions': len(Question.query.all())
        })

    except:
      abort(422)

#### ERROR HANDLERS ################################################

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request(400)"
      }), 400

  @app.errorhandler(404)
  def resourse_not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Resource Not Found(404)"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable(422)"
      }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method Not Allowed'
      })

  '''

  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  done √
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  done √
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  done √
  '''


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

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


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

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

app = create_app()

if __name__ == '__main__':
    app.run()
    
