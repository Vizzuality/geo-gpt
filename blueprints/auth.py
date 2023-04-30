from flask import jsonify, Blueprint
from flask_httpauth import HTTPTokenAuth
import os

auth = Blueprint('auth', __name__)

token_auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    os.getenv('API_TOKEN'): 'user'
}

@token_auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

@token_auth.error_handler
def auth_error():
    return jsonify({'error': 'Unauthorized access'}), 401
