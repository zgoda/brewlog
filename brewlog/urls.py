from brewlog.views.main import main
from brewlog.users.views import select_provider, profile, dashboard, logout, remote_login, google_remote_login_callback, facebook_remote_login_callback
from brewlog.brewing.views import brewery_add

rules = [
    ('/auth/select', dict(endpoint='auth-select-provider', view_func=select_provider)),
    ('/auth/<provider>', dict(endpoint='auth-login', view_func=remote_login)),
    ('/auth/google/callback', dict(endpoint='auth-callback-google', view_func=google_remote_login_callback)),
    ('/auth/facebook/callback', dict(endpoint='auth-callback-facebook', view_func=facebook_remote_login_callback)),
    ('/logout', dict(endpoint='auth-logout', view_func=logout)),
    ('/profile', dict(endpoint='profile', view_func=profile)),
    ('/profile/<userid>', dict(endpoint='profile-details', view_func=dashboard)),
    ('/brewery/add', dict(endpoint='brewery-add', view_func=brewery_add)),
    #('/brewery/all', dict(endpoint='brewery-all')),
    #('/brewery/list', dict(endpoint='brewery-list')),
    #('/brewery/<keyid>', dict(endpoint='brewery-details')),
    #('/brew/list', dict(endpoint='brew-list')),
    #('/brew/add', dict(endpoint='brew-add')),
    #('/brew/<keyid>', dict(endpoint='brew-details')),
    ('/', dict(endpoint='main', view_func=main)),
]
