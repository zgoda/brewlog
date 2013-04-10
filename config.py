import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
SECRET_KEY = 'xxx' # os.urandom(64)
SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
SQLALCHEMY_ECHO = False
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'yyy' # os.urandom(24)

try:
    from config_local import *
except ImportError:
    pass

try:
    from secrets import *
except ImportError:
    pass
