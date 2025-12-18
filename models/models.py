from sqlalchemy import Column, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from controllers.db import DB, Base
from datetime import datetime


class CRUDMixin:
    def save(self):
        DB.add(self)
        DB.commit()
        return self

    def delete(self):
        DB.delete(self)
        DB.commit()
        return self


class User(Base, CRUDMixin):
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


class Midnight(Base, CRUDMixin):
    __tablename__ = 'midnight'
    id = Column(Integer, primary_key=True)
    editor = Column(Text)
    seconds = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    edited_file = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, editor, seconds, start, end, file, user: User):
        self.editor = editor
        self.seconds = seconds
        self.start_date = datetime.strptime(start, '%b-%d_%H:%M:%S')
        self.end_date = datetime.strptime(end, '%b-%d_%H:%M:%S')
        self.edited_file = file
        self.user_id = user.id

    def __repr__(self):
        return f'<Midnight {self.edited_file!r} \
                {self.start_date!r}-{self.end_date}>'
