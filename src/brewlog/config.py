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
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN') or 'unknown'
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY') or 'invalid'
EMAIL_SENDER = f'brewlog@{MAILGUN_DOMAIN}'
EMAIL_CONFIRM_MAX_AGE = PASSWORD_RESET_MAX_AGE = 60 * 60 * 24 * 2

# flatpages
FLATPAGES_EXTENSION = '.html.md'
FLATPAGES_MARKDOWN_EXTENSIONS = []

# display limits
SHORTLIST_DEFAULT_LIMIT = 5
LIST_DEFAULT_LIMIT = 10

# tools
ROLLUP_PATH = os.getenv('ROLLUP_PATH') or 'rollup'
ROLLUP_CONFIG_JS = os.getenv('ROLLUP_CONFIG_JS')
