from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from authlib.flask.client import OAuth

login_manager = LoginManager()

babel = Babel()

pages = FlatPages()

db = SQLAlchemy()

csrf = CSRFProtect()

bootstrap = Bootstrap()

oauth = OAuth()
