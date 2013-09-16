import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
SECRET_KEY = os.urandom(64)
TEST_SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_ECHO = False
CSRF_ENABLED = True
WTF_CSRF_ENABLED = CSRF_ENABLED
CSRF_SESSION_KEY = os.urandom(24)

# file uploads
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2 MiB
ALLOWED_EXTENSIONS = set(['xml'])

# babel
BABEL_DEFAULT_LOCALE = 'pl'
BABEL_DEFAULT_TIMEZONE = 'Europe/Warsaw'

# emails
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True


if 'OPENSHIFT_DATA_DIR' in os.environ:
    try:
        from config_openshift import *
    except ImportError:
        pass

try:
    from config_local import *
except ImportError:
    pass

try:
    from secrets import *
except ImportError:
    pass
