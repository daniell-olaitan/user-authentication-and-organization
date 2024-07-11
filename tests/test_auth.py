#!/usr/bin/python3
"""
Implements unit and end to end tests for the application
"""
import time
import unittest
from flask import jsonify
from models.user import User
from app import create_app
from models import db
from unittest.mock import patch
from datetime import timedelta
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import get_jwt_identity

app = create_app('testing')


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    return jsonify({
        'status': 'success',
        'message': 'Successful',
        'identity': identity
    }), 201

class TestTokenGeneration(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_token_expiration(self):
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=1)
        with self.app.test_request_context():
            access_token = create_access_token(identity='testuser')

        # Attempt to access protected endpoint with valid token
        response = self.test_client.get(
            '/protected',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual('Successful', response.get_json()['message'])

        # Move time forward to simulate token expiration
        expired_time = self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] + timedelta(seconds=1)
        time.sleep(expired_time.seconds)

        # Attempt to access protected endpoint with expired token
        response = self.test_client.get(
            '/protected',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual('The token has expired', response.get_json()['message'])

    def test_user_details_in_token(self):
        response = self.test_client.post(
            '/auth/register',
            json={
                "firstName": "Daniel",
                "lastName": "Olaitan",
                "email": "daniell.olaitan@gmail.com",
                "password": "Uu_2389913116",
                "phone": "+2348084078357"
            },
        )

        response = response.get_json()
        user_id = response['data']['user']['userId']
        access_token = response['data']['accessToken']

        response = self.test_client.get(
            '/protected',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(user_id, response.get_json()['identity'])


class TestOrganizationAccess(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_organization_access(self):
        user1 = self.test_client.post(
            '/auth/register',
            json={
                "firstName": "Daniel",
                "lastName": "Olaitan",
                "email": "daniell.olaitan@gmail.com",
                "password": "Uu_2389913116",
                "phone": "+2348084078357"
            },
        ).get_json()

        user2 = self.test_client.post(
            '/auth/register',
            json={
                "firstName": "Daniel",
                "lastName": "Olaitan",
                "email": "daniell.olaitan@gmail.cm",
                "password": "Uu_2389913116",
                "phone": "+2348084078357"
            },
        ).get_json()

        access_token1 = user1['data']['accessToken']
        access_token2 = user2['data']['accessToken']

        organisation = self.test_client.post(
            '/api/organisations',
            json={
                "name": "Test Organisation"
            },
            headers={
                'Authorization': f"Bearer {access_token1}"
            }
        ).get_json()

        org_id = organisation['data']['orgId']
        response = self.test_client.get(
            f"/api/organisations/{org_id}",
            headers={'Authorization': f'Bearer {access_token1}'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual("Test Organisation", response.get_json()['data']['name'])

        response = self.test_client.get(
            f"/api/organisations/{org_id}",
            headers={'Authorization': f'Bearer {access_token2}'}
        )

        self.assertEqual(response.status_code, 404)


class TestUserRegistrationAndLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_details = {
            "firstName": "Daniel",
            "lastName": "Olaitan",
            "email": "daniell.olaitan@gmail.com",
            "password": "Uu_2389913116",
            "phone": "+2348084078357"
        }

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        response = self.test_client.post(
            '/auth/register',
            json=self.user_details,
        )

        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)

        user = User.query.filter_by(userId=response_json['data']['user']['userId']).first()
        self.assertEqual(user.organizations[0].name, "Daniel's Organisation")

        user = response_json['data']['user']
        for detail_key in self.user_details.keys():
            if detail_key == 'password':
                continue

            with self.subTest(detail_key=detail_key):
                self.assertEqual(user[detail_key], self.user_details[detail_key])

    def test_user_login(self):
        login_details = {
            'email': self.user_details['email'],
            'password': self.user_details['password']
        }

        response = self.test_client.post(
            '/auth/register',
            json=self.user_details,
        )

        response = self.test_client.post(
            '/auth/login',
            json=login_details,
        )
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        user = response_json['data']['user']
        for detail_key in self.user_details.keys():
            if detail_key == 'password':
                continue

            with self.subTest(detail_key=detail_key):
                self.assertEqual(user[detail_key], self.user_details[detail_key])

        test_cases = [
            {
                'email': 'danmmy@gmail.com',
                'password': 'Uu_2389913116',
            },
            {
                'email': 'daniell.olaitan@gmail.com',
                'password': 'Uu_2389913112',
            }
        ]

        for test_case in test_cases:
            response = self.test_client.post(
                '/auth/login',
                json={
                    'email': test_case['email'],
                    'password': test_case['password'],
                }
            )
            self.assertEqual(response.status_code, 401)

    def test_user_validation(self):
        for detail_key in self.user_details.keys():
            if detail_key == 'phone':
                continue

            details = {key: value for key, value in self.user_details.items() if key != detail_key}
            response = self.test_client.post(
                '/auth/register',
                json=details,
            )
            response_json = response.get_json()
            with self.subTest(detail_key=detail_key):
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response_json['errors'][0]['field'], detail_key)

    def test_email_validation(self):
        response = self.test_client.post(
            '/auth/register',
            json=self.user_details,
        )

        response = self.test_client.post(
            '/auth/register',
            json=self.user_details,
        )
        response_json = response.get_json()
        self.assertEqual(response.status_code, 422)
        self.assertIn(response_json['errors'][0]['message'], 'Email must be unique')
