from brewlog.views.main import main
from brewlog.users.views import select_provider, profile, logout, remote_login, remote_login_callback

rules = [
    ('/auth/select', dict(endpoint='auth-select-provider', view_func=select_provider)),
    ('/auth/<provider>', dict(endpoint='auth-login', view_func=remote_login)),
    ('/auth/<provider>/callback', dict(endpoint='auth-callback', view_func=remote_login_callback)),
    ('/logout', dict(endpoint='auth-logout', view_func=logout)),
    ('/profile', dict(endpoint='profile', view_func=profile)),
    #('/profile/<keyid>', dict(endpoint='profile-details')),
    #('/brewery/add', dict(endpoint='brewery-add')),
    #('/brewery/all', dict(endpoint='brewery-all')),
    #('/brewery/list', dict(endpoint='brewery-list')),
    #('/brewery/<keyid>', dict(endpoint='brewery-details')),
    #('/brew/list', dict(endpoint='brew-list')),
    #('/brew/add', dict(endpoint='brew-add')),
    #('/brew/<keyid>', dict(endpoint='brew-details')),
    ('/', dict(endpoint='main', view_func=main)),
]
