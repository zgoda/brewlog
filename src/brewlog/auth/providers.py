from flask import session

from ..ext import oauth


def get_access_token():  # pragma: nocover
    return session.get('access_token')


facebook = oauth.register('facebook', fetch_token=get_access_token)
google = oauth.register('google', fetch_token=get_access_token)
github = oauth.register('github', fetch_token=get_access_token)
