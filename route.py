# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from webapp2 import Route

routes = [
    Route(r'/auth/select', handler='handlers.AuthHandler', handler_method='select_auth', name='auth-select-provider'),
    Route(r'/auth/<provider>', handler='handlers.AuthHandler', handler_method='_simple_auth', name='auth-login'),
    Route(r'/auth/<provider>/callback', handler='handlers.AuthHandler', handler_method='_auth_callback', name='auth-callback'),
    Route(r'/logout', handler='handlers.AuthHandler', handler_method='logout', name='auth-logout'),
    Route(r'/profile', handler='handlers.ProfileHandler', handler_method='my_profile', name='profile'),
    Route(r'/profile/<keyid>', handler='handlers.ProfileHandler', handler_method='view_details', name='profile-details'),
    Route(r'/brewery/add', handler='handlers.BreweryHandler', handler_method='add_brewery', name='brewery-add'),
    Route(r'/brewery/all', handler='handlers.BreweryHandler', handler_method='all_breweries', name='brewery-all'),
    Route(r'/brewery/list', handler='handlers.BreweryHandler', handler_method='list_breweries', name='brewery-list'),
    Route(r'/brewery/<keyid>', handler='handlers.BreweryHandler', handler_method='brewery_details', name='brewery-details'),
    Route(r'/', handler='handlers.MainHandler', name='main'),
]
