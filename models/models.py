from flask_login import UserMixin
from sqlalchemy import Column, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from controllers.db import DB, Base


class CRUDMixin:
    def save(self):
        DB.add(self)
        DB.commit()
        return self

    def delete(self):
        DB.delete(self)
        DB.commit()
        return self


class User(Base, CRUDMixin, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    api_key = Column(Text, unique=True, nullable=False)
    midnights = relationship('Midnight')

    def __init__(self, username, password, api_key):
        self.username = username
        self.password = password
        self.api_key = api_key

    def __repr__(self):
        return f'<User {self.username!r}>'


class Midnight(Base):
    __tablename__ = 'midnight'
    id = Column(Integer, primary_key=True)
    editor = Column(Text)
    seconds = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    edited_file = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
