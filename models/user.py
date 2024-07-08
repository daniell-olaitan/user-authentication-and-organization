#!/usr/bin/python3
"""
Creates the user model
"""
import uuid
from models import db
from hashlib import md5
from models.base_model import BaseModel


class User(BaseModel, db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.String(60), primary_key=True, nullable=False, unique=True)
    firstName = db.Column(db.String(60), nullable=False)
    lastName = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userId = str(uuid.uuid4())
        password_hash = md5(kwargs['password'].encode('utf-8'))
        self.password = password_hash.hexdigest()

    @classmethod
    def validate_user_details(cls, details):
        # email_regex = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)"
        # "*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

        errors = {
            'errors': []
        }

        if not details.get('firstName'):
            error = {
                'field': 'firstName',
                'message': 'First name is required'
            }
            errors['errors'].append(error)

        if not details.get('lastName'):
            error = {
                'field': 'lastName',
                'message': 'Last name is required'
            }
            errors['errors'].append(error)

        if not details.get('email'):
            error = {
                'field': 'email',
                'message': 'Email is required and must be unique'
            }
            errors['errors'].append(error)
        else:
            user = cls.query.filter_by(email=details['email']).first()
            if user:
                error = {
                    'field': 'email',
                    'message': 'Email must be unique'
                }
                errors['errors'].append(error)

        if not details.get('password'):
            error = {
                'field': 'password',
                'message': 'Password is required'
            }
            errors['errors'].append(error)

        if errors['errors']:
            return errors
        return False

    @classmethod
    def validate_login_details(cls, details):
        errors = {
            'errors': []
        }

        if not details.get('email'):
            error = {
                'field': 'email',
                'message': 'Email is required'
            }
            errors['errors'].append(error)

        if not details.get('password'):
            error = {
                'field': 'password',
                'message': 'Password is required'
            }
            errors['errors'].append(error)

        if errors['errors']:
            return errors
        return False

    def authenticate_user(self, password):
        password_hash = md5(password.encode('utf-8'))
        if password_hash.hexdigest() == self.password:
            return True
        return False
