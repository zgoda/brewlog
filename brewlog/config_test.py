TESTING = True
BABEL_DEFAULT_LOCALE = 'en_US'
CSRF_ENABLED = False
WTF_CSRF_ENABLED = CSRF_ENABLED
LOGIN_DISABLED = False
SQLALCHEMY_DATABASE_URI = 'sqlite://'

AUTH_CONFIG = {
    'google': ('app_id', 'app_secret'),
    'facebook': ('app_id', 'app_secret'),
    'github': ('app_id', 'app_secret'),
}
