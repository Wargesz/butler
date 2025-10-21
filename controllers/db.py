from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:///butler.sqlite')

# session
DB = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine))

Base = declarative_base()
Base.query = DB.query_property()


def setup_db():
    from models.models import User, Midnight
    Base.metadata.create_all(bind=engine)
