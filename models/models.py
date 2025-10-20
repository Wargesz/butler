from flask_login import UserMixin
from app import app

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    password = Column(Text)
    api_key = Column(Text, unique=True)
    midnights = relationship('Midnight')

    def __init__(self, name, password, api_key):
        self.name = name
        self.password = password
        self.api_key = api_key

    def __repr(self):
        return f'<User {self.name!r}>'


class Midnight(Base):
    __tablename__ = 'midnight'
    id = Column(Integer, primary_key=True)
    editor = Column(Text)
    seconds = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    edited_file = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
