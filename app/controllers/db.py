from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

DATABASE = "butler.db"
engine = create_engine(f'sqlite:///{DATABASE}')
db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import modules here
    import app.models.models
    Base.metadata.create_all(bind=engine)


def get_engine():
    return engine
