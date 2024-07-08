#!/usr/bin/python3
"""
Instantiates the api blueprint of the application
"""
from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from app.api.views import *
