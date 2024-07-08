#!/usr/bin/python3
"""
Instantiates the auth blueprint of the application
"""
from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth.views import *
