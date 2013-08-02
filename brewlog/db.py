from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, create_session
from sqlalchemy.ext.declarative import declarative_base


engine = None

def init_engine(uri, **kwargs):
    global engine
    engine = create_engine(uri, **kwargs)
    return engine

session = scoped_session(lambda: create_session(
    bind=engine,
    autocommit=False,
    autoflush=True,
    expire_on_commit=True,
))

Model = declarative_base(bind=engine)
Model.query = session.query_property()

def init_db():
    import models
    Model.metadata.create_all(bind=engine)

def clear_db():
    import models
    Model.metadata.drop_all(bind=engine)
