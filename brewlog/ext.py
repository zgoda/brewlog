from flask_login import LoginManager
login_manager = LoginManager()

from flask_babelex import Babel
babel = Babel()

from flask_flatpages import FlatPages
pages = FlatPages()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_wtf.csrf import CsrfProtect
csrf = CsrfProtect()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()
