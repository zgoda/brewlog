import os

from flask import session

from ..ext import oauth


def get_access_token():  # pragma: nocover
    return session.get('access_token')


facebook = oauth.register(
    'facebook',
    client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
    client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET'),
    api_base_url='https://graph.facebook.com/v2.12',
    access_token_url='https://graph.facebook.com/v2.12/oauth/access_token',
    authorize_url='https://www.facebook.com/v2.12/dialog/oauth',
    access_token_method='POST',
    client_kwargs={'scope': 'email public_profile'},
    fetch_token=get_access_token,
)

google = oauth.register(
    'google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    api_base_url='https://www.googleapis.com',
    access_token_url='https://www.googleapis.com/oauth2/v4/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth?access_type=offline',
    access_token_method='POST',
    client_kwargs={'scope': 'openid email profile'},
    fetch_token=get_access_token
)

github = oauth.register(
    'github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    api_base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_method='POST',
    client_kwargs={'scope': 'user:email'},
    fetch_token=get_access_token
)
