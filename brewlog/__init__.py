from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config.from_object('config')

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base()
Model.query = session.query_property()

def init_db():
    import brewing.models
    import users.models
    Model.metadata.create_all(bind=engine)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
