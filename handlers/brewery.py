# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.api import users

from handlers.base import BaseRequestHandler


class BreweryHandler(BaseRequestHandler):

    def list_breweries(self):
        user = users.get_current_user()
