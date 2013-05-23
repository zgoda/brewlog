from brewlog.utils.routing import LazyView

rules = [
    ('/auth/select',
        dict(endpoint='auth-select-provider', view_func=LazyView('brewlog.users.views.select_provider'))),
    ('/auth/<provider>',
        dict(endpoint='auth-login', view_func=LazyView('brewlog.users.views.remote_login'))),
    ('/auth/google/callback',
        dict(endpoint='auth-callback-google', view_func=LazyView('brewlog.users.views.google_remote_login_callback'))),
    ('/auth/facebook/callback',
        dict(endpoint='auth-callback-facebook', view_func=LazyView('brewlog.users.views.facebook_remote_login_callback'))),
    ('/logout',
        dict(endpoint='auth-logout', view_func=LazyView('brewlog.users.views.logout'))),
    ('/profile/<userid>',
        dict(endpoint='profile-details', view_func=LazyView('brewlog.users.views.profile'), methods=['POST', 'GET'])),
    ('/brewery/add',
        dict(endpoint='brewery-add', view_func=LazyView('brewlog.brewing.views.brewery_add'), methods=['POST', 'GET'])),
    ('/brewery/all',
        dict(endpoint='brewery-all', view_func=LazyView('brewlog.brewing.views.brewery_all'))),
    ('/brewery/<brewery_id>',
        dict(endpoint='brewery-details', view_func=LazyView('brewlog.brewing.views.brewery'), methods=['POST', 'GET'])),
    ('/brew/add',
        dict(endpoint='brew-add', view_func=LazyView('brewlog.brewing.views.brew_add'), methods=['POST', 'GET'])),
    ('/brew/all',
        dict(endpoint='brew-all', view_func=LazyView('brewlog.brewing.views.brew_all'))),
    ('/brew/<brew_id>',
        dict(endpoint='brew-details', view_func=LazyView('brewlog.brewing.views.brew'), methods=['POST', 'GET'])),
    ('/',
        dict(endpoint='main', view_func=LazyView('brewlog.views.main'))),
]