#!/usr/bin/python3
"""
Defines a model for revoked tokens
"""
import uuid
from models import db


class InvalidToken(db.Model):
    __tablename__ = 'invalid_token'
    tokenId = db.Column(db.String(60), primary_key=True, nullable=False, unique=True)
    jti = db.Column(db.String(36), nullable=False, index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tokenId = str(uuid.uuid4())

    @classmethod
    def verify_jti(cls, jti):
        """checks if the token is blacklisted"""
        return bool(cls.query.filter_by(jti=jti).first())
