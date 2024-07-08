#!/usr/bin/python3
"""
defines the organization model of the organization
"""
import uuid
from models import db
from models.base_model import BaseModel

user_organization = db.Table('user_organization',
    db.Column('orgId', db.String(60), db.ForeignKey('users.userId')),
    db.Column('userId', db.String(60), db.ForeignKey('organizations.orgId'))
)


class Organization(BaseModel, db.Model):
    __tablename__ = 'organizations'
    orgId = db.Column(db.String(60), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(2048))
    users = db.relationship('User', backref='organizations', secondary=user_organization)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orgId = str(uuid.uuid4())
