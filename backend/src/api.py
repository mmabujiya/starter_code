import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def retrieve_drinks():
    
    drinks = Drink.query.all()
    drink_short = [drink.short() for drink in drinks]
        
    return jsonify({
        "success": True,
        "drinks": drink_short
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# @app.route('/drinks-detail', Methods=['GET'])
# # @requires_auth('get:drinks-detail')
# def retrieve_drinks_details(payload):
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(payload):
    
    drinks = Drink.query.all()
    drink_detiail = [drink.long() for drink in drinks]
        
    return jsonify({
        "success": True,
        "drinks": drink_detiail
    }), 200

    
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    if not new_title and new_recipe:
        abort(401)
    # call the database
    drink = Drink(title = new_title, recipe = json.dumps(new_recipe))
    
    # insert into the database with the .dumps to convert to json string
    drink.insert()

    return jsonify({
                "success": True,
                "drinks": [drink.long()]
    }), 200


# '''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):

        body = request.get_json()

        
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink_id is None:
            abort(404)

        if 'title' or 'recipe' in body:
            get_title = body.get('title')
            drink.title = get_title
            get_recipe = body.get('recipe')
            # to convert to json string
            drink.recipe = json.dumps(get_recipe)

            drink.update()
            updated_drink = [drink.long()]

        return jsonify(
            {
                "success": True, 
                "drinks": updated_drink
        }), 200
    

# '''
# @TODO implement endpoint
#     DELETE /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should delete the corresponding row for <id>
#         it should require the 'delete:drinks' permission
#     returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
#         or appropriate status code indicating reason for failure
# '''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):

            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

            if drink_id is None:
                abort(404)

            drink.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": drink_id
                }
            ), 200
       
# # Error Handling
# '''
# Example error handling for unprocessable entity
# '''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# '''
# @TODO implement error handlers using the @app.errorhandler(error) decorator
#     each error handler should return (with approprate messages):
#              jsonify({
#                     "success": False,
#                     "error": 404,
#                     "message": "resource not found"
#                     }), 404

# '''

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
    "success": False, 
    "error": 404,
    "message": "resource not found"
    }), 404



'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response