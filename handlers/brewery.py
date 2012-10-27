# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.api import users

from handlers.base import BaseRequestHandler
from models.base import Brewery


class BreweryHandler(BaseRequestHandler):

    def list_breweries(self):
        current_user = users.get_current_user()
        bl = Brewery.query(Brewery.user == current_user)
        ctx = {
        	'breweries': bl,
        	'user': current_user,
        }
        self.render_to_response('brewery/list.html', **ctx)