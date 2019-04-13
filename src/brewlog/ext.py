# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from authlib.flask.client import OAuth

from .utils.models import Model

login_manager = LoginManager()

babel = Babel()

pages = FlatPages()

db = SQLAlchemy(model_class=Model)

csrf = CSRFProtect()

bootstrap = Bootstrap()

oauth = OAuth()
