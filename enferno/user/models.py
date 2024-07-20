import dataclasses
from typing import Dict

from sqlalchemy import Integer, Column, ForeignKey, Table

from enferno.extensions import db
from enferno.utils.base import BaseMixin

roles_users: Table = db.Table(
    'roles_users',
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True)
)


@dataclasses.dataclass
class Role(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def from_dict(self, json_dict):
        self.name = json_dict.get('name', self.name)
        self.description = json_dict.get('description', self.description)
        return self


@dataclasses.dataclass
class User(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=False, nullable=True)





    def to_dict(self):
        return {
            'id': self.id,
            'active': self.active,
            'name': self.name,
            'username': self.username,
            'email': self.email,
        }



    def __str__(self) -> str:
        """
        Return the string representation of the object, typically using its ID.
        """
        return f'{self.id}'

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the object.
        """
        return f"{self.username} {self.id} {self.email}"

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'email', 'username'],
        'ordering': ['-created_at']
    }

