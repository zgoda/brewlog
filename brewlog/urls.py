from brewlog.views.main import main
from brewlog.users.views import select_provider, profile, dashboard, logout, remote_login, google_remote_login_callback, facebook_remote_login_callback
from brewlog.brewing.views import brewery_add, brewery_all, brewery_details, brew_add, brew_details

rules = [
    ('/auth/select', dict(endpoint='auth-select-provider', view_func=select_provider)),
    ('/auth/<provider>', dict(endpoint='auth-login', view_func=remote_login)),
    ('/auth/google/callback', dict(endpoint='auth-callback-google', view_func=google_remote_login_callback)),
    ('/auth/facebook/callback', dict(endpoint='auth-callback-facebook', view_func=facebook_remote_login_callback)),
    ('/logout', dict(endpoint='auth-logout', view_func=logout)),
    ('/profile', dict(endpoint='profile', view_func=profile)),
    ('/profile/<userid>', dict(endpoint='profile-details', view_func=dashboard, methods=['POST', 'GET'])),
    ('/brewery/add', dict(endpoint='brewery-add', view_func=brewery_add, methods=['POST', 'GET'])),
    ('/brewery/all', dict(endpoint='brewery-all', view_func=brewery_all)),
    #('/brewery/list', dict(endpoint='brewery-list')),
    ('/brewery/<brewery_id>', dict(endpoint='brewery-details', view_func=brewery_details, methods=['POST', 'GET'])),
    #('/brew/list', dict(endpoint='brew-list')),
    ('/brew/add', dict(endpoint='brew-add', view_func=brew_add, methods=['POST', 'GET'])),
    ('/brew/<brew_id>', dict(endpoint='brew-details', view_func=brew_details, method=['POST', 'GET'])),
    ('/', dict(endpoint='main', view_func=main)),
]
