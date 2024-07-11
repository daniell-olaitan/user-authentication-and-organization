#!/usr/bin/python3
"""
Implements the view functions of the auth blueprint
"""
from flask import request, jsonify
from app.auth import auth
from models import db
from models.user import User
from models.organization import Organization
from flask_jwt_extended import create_access_token
from models.invalid_tokens import InvalidToken
from app import jwt


@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return InvalidToken.verify_jti(jti)


@auth.route('/register', methods=['POST'])
def register_user():
    try:
        user_details = request.get_json()
        user_validation_errors = User.validate_user_details(user_details)
        if user_validation_errors:
            return jsonify(user_validation_errors), 422

        organization = Organization(
            name=user_details['firstName']+"'s"+' Organization',
            description=None
        )
        user = User(**user_details)
        user.organizations.append(organization)
        db.save(user)

        access_token = create_access_token(identity=user.userId)
        payload = {
            'status': 'success',
            'message': 'Registration successful',
            'data': {
                'accessToken': access_token,
                'user': user.to_json()
            }
        }

        return jsonify(payload), 201
    except:
        return jsonify({
            'status': 'Bad request',
            'message': 'Registration unsuccessful',
            'statusCode': 400
        }), 400


@auth.route('/login', methods=['POST'])
def login():
    error_payload ={
        'status': 'Bad request',
        'message': 'Authentication failed',
        'statusCode': 401
    }

    try:
        login_details = request.get_json()
        login_validation_errors = User.validate_login_details(login_details)
        if login_validation_errors:
            return jsonify(login_validation_errors), 422

        user = User.query.filter_by(email=login_details['email']).first()
        if user:
            if user.authenticate_user(login_details['password']):
                access_token = create_access_token(identity=user.userId)
                user_details = user.to_json()
                payload = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'accessToken': access_token,
                        'user': user_details
                    }
                }

                return jsonify(payload), 200
            else:
                return jsonify(error_payload), 401
        else:
            return jsonify(error_payload), 401
    except:
        return jsonify(error_payload), 401
