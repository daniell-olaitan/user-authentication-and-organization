#!/usr/bin/python3
"""
Configuration file for the project
"""
from os import getenv
from datetime import timedelta


class Config:
    """
    Class defines the common configurations of the project
    """
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=10)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']


class DevelopmentConfig(Config):
    """
    Class defines the configurations that are specific to development
    """
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
        getenv('DATABASE_USERNAME'),
        getenv('DATABASE_PASSWORD'),
        getenv('DATABASE_HOST'),
        getenv('DATABASE_PORT'),
        getenv('DATABASE'))


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig
}
