import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
SECRET_KEY = 'not so secret'
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True
WTF_CSRF_ENABLED = CSRF_ENABLED
CSRF_SESSION_KEY = 'not so secret'

# flatpages
FLATPAGES_EXTENSION = '.html.md'
FLATPAGES_MARKDOWN_EXTENSIONS = []

# babel
BABEL_DEFAULT_LOCALE = 'pl'
BABEL_DEFAULT_TIMEZONE = 'Europe/Warsaw'

# display limits
SHORTLIST_DEFAULT_LIMIT = 5
LIST_DEFAULT_LIMIT = 10

AUTH_CONFIG = {
    'google': ('app_id', 'app_secret'),
    'facebook': ('app_id', 'app_secret'),
    'github': ('app_id', 'app_secret'),
}

try:
    from .secrets.config_local import *  # noqa
except ImportError:
    pass

try:
    from .secrets.secrets import *  # noqa
except ImportError:
    pass
