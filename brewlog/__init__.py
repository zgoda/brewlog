import os

from flask import Flask, render_template, get_flashed_messages
from flaskext.babel import Babel, lazy_gettext as _
from flask_login import LoginManager, current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
app.config.from_object('brewlog.config')
if os.environ.get('BREWLOG_CONFIG', ''):
    app.config.from_envvar('BREWLOG_CONFIG')

# i18n
babel = Babel(app)

# database
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
    convert_unicode=True,
    echo=app.config['SQLALCHEMY_ECHO']
)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base(bind=engine)
Model.query = session.query_property()

def init_db():
    import models
    Model.metadata.create_all(bind=engine)

def clear_db():
    import models
    Model.metadata.drop_all(bind=engine)

# login infrastructure
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth-select-provider'
login_manager.login_message = _('Please log in to access this page')
login_manager.login_message_category = 'info'

@login_manager.user_loader
def get_user(userid):
    from models import BrewerProfile
    return BrewerProfile.query.get(userid)

# register url map
from brewlog.urls import rules
for url, kwargs in rules:
    app.add_url_rule(url, **kwargs)

# app-level event handlers
@app.teardown_request
def shutdown_session(exception=None):
    session.remove()

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.context_processor
def inject():
    return {
        'DEV': app.config['DEBUG'],
        'user': current_user,
        'flashes': get_flashed_messages(),
    }

# templates
def register_filters(application):
    from utils import templates
    application.jinja_env.globals['url_for_other_page'] = templates.url_for_other_page
    import math
    application.jinja_env.globals['pow'] = math.pow

register_filters(app)
