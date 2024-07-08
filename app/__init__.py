#!/usr/bin/python3
"""
implements the factory function to create and initialize the application
"""
from dotenv import load_dotenv
load_dotenv()

from models import db
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config

migrate = Migrate()
jwt = JWTManager()



def create_app(config_type):
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config[config_type])
    from app.auth import auth
    from app.api import api
    app.register_blueprint(auth)
    app.register_blueprint(api)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    with app.app_context():
        db.create_all()

    return app
