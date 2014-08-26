from flask import session
from flask.ext.oauthlib.client import OAuth

try:
    from brewlog.secrets import AUTH_CONFIG
except ImportError:
    AUTH_CONFIG = {
        'google': ('app_id', 'app_secret'),
        'facebook': ('app_id', 'app_secret'),
        'github': ('app_id', 'app_secret'),
    }


oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=AUTH_CONFIG['facebook'][0],
    consumer_secret=AUTH_CONFIG['facebook'][1],
    request_token_params={'scope': 'email'},
)

google = oauth.remote_app('google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
        'scope': [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/calendar',
        ],
    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    consumer_key=AUTH_CONFIG['google'][0],
    consumer_secret=AUTH_CONFIG['google'][1],
)

github = oauth.remote_app('github',
    consumer_key=AUTH_CONFIG['github'][0],
    consumer_secret=AUTH_CONFIG['github'][1],
    request_token_params={
        'scope': 'user:email',
    },
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
)

services = {
    'google': (google, 'oauth2'),
    'facebook': (facebook, 'oauth2'),
    'github': (github, 'oauth2'),
    'local': (None, None),
}


@google.tokengetter
@facebook.tokengetter
@github.tokengetter
def get_access_token():  # pragma: no cover
    return session.get('access_token')
