import os

# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here:
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = '\x01\xe5\x1a\xdc\xd6:\x805/\xd0\x8bL\xb0`J\x07C^%\xc2;\x1b\xbeV4\xe1X\x8fH\xd6\x0erY\xa4t\xaa\xaa\xc6^\xe1V\xeat\x92AM\xdd\x018\xd9D#\x1f\xe9\xee?\xc3\xb6\x87[\xd1IA\xe8'

# Google APIs
GOOGLE_APP_ID = 'app id'
GOOGLE_APP_SECRET = 'app secret'

# Facebook auth apis
FACEBOOK_APP_ID = 'app id'
FACEBOOK_APP_SECRET = 'app secret'

# https://www.linkedin.com/secure/developer
LINKEDIN_CONSUMER_KEY = 'consumer key'
LINKEDIN_CONSUMER_SECRET = 'consumer secret'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = 'client id'
WL_CLIENT_SECRET = 'client secret'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'oauth1.0a consumer key'
TWITTER_CONSUMER_SECRET = 'oauth1.0a consumer secret'

# config that summarizes the above
AUTH_CONFIG_PROD = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me'),
  'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET),

  # OpenID doesn't need any key/secret
}

AUTH_CONFIG_DEV = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me'),
  'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET),

  # OpenID doesn't need any key/secret
}

if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    AUTH_CONFIG = AUTH_CONFIG_DEV
else:
    AUTH_CONFIG = AUTH_CONFIG_PROD

