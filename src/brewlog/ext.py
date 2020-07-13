from flask_assets import Environment
from flask_babel import Babel
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from .utils.models import Model

login_manager = LoginManager()
babel = Babel()
pages = FlatPages()
db = SQLAlchemy(model_class=Model)
csrf = CSRFProtect()
migrate = Migrate()
assets = Environment()
