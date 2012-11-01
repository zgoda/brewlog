# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from webapp2 import Route

routes = [
    Route(r'/auth/<provider>', handler='handlers.AuthHandler', handler_method='_simple_auth', name='auth-login'),
    Route(r'/auth/<provider>/callback', handler='handlers.AuthHandler', handler_method='_auth_callback', name='auth-callback'),
    Route(r'/logout', handler='handlers.AuthHandler', handler_method='logout', name='auth-logout'),
    Route(r'/profile', handler='handlers.ProfileHandler', name='profile'),
    Route(r'/brewery/add', handler='handlers.BreweryHandler', handler_method='add_brewery', name='brewery-add'),
    Route(r'/brewery/<keyid>', handler='handlers.BreweryHandler', handler_method='brewery_details', name='brewery-details'),
    Route(r'/brewery', handler='handlers.BreweryHandler', handler_method='list_breweries', name='brewery-main'),
    Route(r'/', handler='handlers.MainHandler', name='main'),
]
