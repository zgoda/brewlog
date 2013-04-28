from flask import Flask, render_template
from flaskext.babel import Babel, lazy_gettext as _
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config.from_object('brewlog.config')
app.config['BABEL_DEFAULT_LOCALE'] = 'pl'
babel = Babel(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
    convert_unicode=True,
    echo=app.config['SQLALCHEMY_ECHO']
)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Model = declarative_base(bind=engine)
Model.query = session.query_property()

# login infrastructure
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'brewlog.users.views.select_provider'
login_manager.login_message = _('Please log in to access this page')
login_manager.login_message_category = 'info'

# register url map
from brewlog.urls import rules
for url, kwargs in rules:
    app.add_url_rule(url, **kwargs)


def init_db():
    import brewing.models
    import users.models
    Model.metadata.create_all(bind=engine)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
