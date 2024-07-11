#!/usr/bin/python3
"""
Module defines the base model class
"""


class BaseModel:
    def to_json(self):
        obj = vars(self)
        if obj.get('_sa_instance_state'):
            del obj['_sa_instance_state']
        if obj.get('password'):
            del obj['password']

        return obj
