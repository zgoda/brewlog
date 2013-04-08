from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import settings

engine = create_engine(settings.DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Model = declarative_base()
Model.query = db_session.query_property()

def init_db():
    import models.sqla
    Model.metadata.create_all(bind=engine)
