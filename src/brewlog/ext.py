import os

from dotenv import find_dotenv, load_dotenv
from flask_assets import Environment
from flask_babel import Babel
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_rollup import Rollup
from huey import SqliteHuey

from .utils.models import Model

load_dotenv(find_dotenv())

instance_path = os.environ['INSTANCE_PATH']
os.makedirs(instance_path, exist_ok=True)

login_manager = LoginManager()
babel = Babel(default_locale='pl', default_timezone='Europe/Warsaw')
pages = FlatPages()
db = SQLAlchemy(model_class=Model)
csrf = CSRFProtect()
migrate = Migrate()
assets = Environment()
rollup = Rollup()

huey = SqliteHuey(filename=os.path.join(instance_path, 'huey.sqlite'))
