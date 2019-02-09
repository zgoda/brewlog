from flask import current_app, session

from ..ext import oauth


def get_access_token():  # pragma: nocover
    return session.get('access_token')


auth_config = current_app.config['AUTH_CONFIG']


facebook = oauth.register(
    'facebook',
    api_base_url='https://graph.facebook.com/v3.2',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/v3.2/dialog/oauth',
    client_id=auth_config['facebook'][0],
    client_secret=auth_config['facebook'][1],
    client_kwargs={
        'scope': 'email'
    },
    fetch_token=get_access_token,
)

google = oauth.register(
    'google',
    api_base_url='https://www.googleapis.com',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    client_kwargs={
        'scope': [
            'https://www.googleapis.com/auth/userinfo.email',
        ],
    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    client_id=auth_config['google'][0],
    client_secret=auth_config['google'][1],
    fetch_token=get_access_token
)

github = oauth.register(
    'github',
    client_id=auth_config['github'][0],
    client_secret=auth_config['github'][1],
    client_kwargs={
        'scope': 'user:email',
    },
    api_base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    fetch_token=get_access_token
)


services = {
    'facebook': facebook,
    'google': google,
    'github': github,
    'local': 'local',
}
