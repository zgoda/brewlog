import os

DEBUG = False
TESTING = False
SECRET_KEY = 'not so secret'
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True
WTF_CSRF_ENABLED = CSRF_ENABLED
CSRF_SESSION_KEY = 'not so secret'
REDIS_URL = os.environ.get('REDIS_URL', 'redis://')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
EMAIL_SENDER = f'brewlog@{MAILGUN_DOMAIN}'
EMAIL_CONFIRM_MAX_AGE = 60 * 60 * 24 * 2

# flatpages
FLATPAGES_EXTENSION = '.html.md'
FLATPAGES_MARKDOWN_EXTENSIONS = []

# babel
BABEL_DEFAULT_LOCALE = 'pl'
BABEL_DEFAULT_TIMEZONE = 'Europe/Warsaw'

# display limits
SHORTLIST_DEFAULT_LIMIT = 5
LIST_DEFAULT_LIMIT = 10

try:
    from .secrets.config_local import *  # noqa
except ImportError:
    pass

try:
    from .secrets.secrets import *  # noqa
except ImportError:
    pass
