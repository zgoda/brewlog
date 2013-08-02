from flask import session
from flask import current_app as app
from flask_oauth import OAuth

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config['AUTH_CONFIG']['facebook'][0],
    consumer_secret=app.config['AUTH_CONFIG']['facebook'][1],
    request_token_params={'scope': 'email'},
)

google = oauth.remote_app('google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'response_type': 'code',
    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key=app.config['AUTH_CONFIG']['google'][0],
    consumer_secret=app.config['AUTH_CONFIG']['google'][1],
)

services = {
    'google': (google, 'oauth2'),
    'facebook': (facebook, 'oauth2'),
    'local': (None, None),
}


@google.tokengetter
@facebook.tokengetter
def get_access_token():
    return session.get('access_token')
