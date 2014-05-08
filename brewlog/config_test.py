TESTING = True
BABEL_DEFAULT_LOCALE = 'en_US'
CSRF_ENABLED = False
WTF_CSRF_ENABLED = CSRF_ENABLED
LOGIN_DISABLED = False

AUTH_CONFIG = {
  'google'      : ('app_id', 'app_secret',
                  'https://www.googleapis.com/auth/userinfo.profile'),
  'facebook'    : ('app_id', 'app_secret',
                  'user_about_me'),
}
