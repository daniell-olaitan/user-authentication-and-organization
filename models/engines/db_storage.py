#!/usr/bin/python3
"""
Module defines the ORM for the database
"""
from flask_sqlalchemy import SQLAlchemy


class DBStorage(SQLAlchemy):
    """Defines the db ORM class"""
    def save(self, obj):
        self.session.add(obj)
        self.session.commit()

    def remove(self, obj):
        self.session.delete(obj)
        self.session.commit()
