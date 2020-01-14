import os

DEBUG = False
TESTING = False
SECRET_KEY = os.environ.get('SECRET_KEY') or 'not-so-secret'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite://'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True
WTF_CSRF_ENABLED = CSRF_ENABLED
CSRF_SESSION_KEY = SECRET_KEY
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN') or 'unknown'
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY') or 'invalid'
EMAIL_SENDER = f'brewlog@{MAILGUN_DOMAIN}'
EMAIL_CONFIRM_MAX_AGE = 60 * 60 * 24 * 2

# flatpages
FLATPAGES_EXTENSION = '.html.md'
FLATPAGES_MARKDOWN_EXTENSIONS = []

# babel
BABEL_DEFAULT_LOCALE = os.getenv('BABEL_DEFAULT_LOCALE') or 'pl'
BABEL_DEFAULT_TIMEZONE = os.getenv('BABEL_DEFAULT_TIMEZONE') or 'Europe/Warsaw'

# display limits
SHORTLIST_DEFAULT_LIMIT = 5
LIST_DEFAULT_LIMIT = 10
