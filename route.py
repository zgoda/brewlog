# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from webapp2 import Route

routes = [
    Route(r'/brewery', handler='handlers.BreweryHandler', handler_method='list_breweries', name='brewery-main'),
    Route(r'/', handler='handlers.MainHandler', name='main'),
]
