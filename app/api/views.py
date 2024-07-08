#!/usr/bin/python3
"""
Implements the view functions of the api blueprint
"""
from flask import request, jsonify, abort
from app.api import api
from models import db
from models.user import User
from models.organization import Organization
from flask_jwt_extended import jwt_required, get_jwt_identity


@api.route('/users/<id>', methods=['GET'])
@jwt_required()
def fetch_a_user(id):
    fetched_user = User.query.filter_by(userId=id).first()
    user_id = get_jwt_identity()
    if fetched_user:
        user_details = fetched_user.to_json()
        payload = {
            'status': 'success',
            'message': 'A user has been fetched successfully',
            'data': user_details
        }

        if fetched_user.userId == user_id:
            return jsonify(payload), 200

        current_user = User.query.filter_by(userId=user_id).first()
        if current_user:
            fetched_user_organizations = fetched_user.organizations
            current_user_organizations = current_user.organizations
            for u in fetched_user_organizations:
                if u in current_user_organizations:
                    return jsonify(payload), 200

    abort(404)


@api.route('/organisations', methods=['GET', 'POST'])
@jwt_required()
def get_organizations():
    user_id = get_jwt_identity()
    user = User.query.filter_by(userId=user_id).first()
    if user:
        organizations = []
        for organization in user.organizations:
            organizations.append(
                organization.to_json()
            )

        return jsonify({
            'status': 'success',
		    'message': "Organizations have been fetched",
            'data': {
            'organisations': organizations
            }
        }), 200

    abort(404)


@api.route('/organisations/<orgId>', methods=['GET'])
@jwt_required()
def get_an_organisation(orgId):
    organization = Organization.query.filter_by(orgId=orgId).first()
    if organization:
        return jsonify({
            'status': 'success',
		    'message': "An organization has been fetched",
            'data': organization.to_json()
        }), 200

    abort(404)


@api.route('/organisations', methods=['POST'])
@jwt_required()
def create_an_organisation():
    error_playload = {
        'status': 'Bad Request',
        'message': 'Client error',
        'statusCode': 400
    }
    user_id = get_jwt_identity()
    try:
        organization_details = request.get_json()
        organization_validation_errors = Organization.validate_organization_details(organization_details)
        if organization_validation_errors:
            return jsonify(organization_validation_errors), 422

        user = User.query.filter_by(userId=user_id).first()
        organization = Organization(**organization_details)
        if organization and user:
            user.organizations.append(organization)
            db.save(user)
            return jsonify({
                'status': 'success',
                'message': "An organization has been fetched",
                'data': organization.to_json()
            }), 200
        else:
            return jsonify(error_playload), 400
    except:
        return jsonify(error_playload), 400
