# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.api import users

import webapp2

from utils.keys import key
from forms.brewery import BreweryForm
from models import Brewery


class BreweryHandler(webapp2.RequestHandler):

    def list_breweries(self):
        user = users.get_current_user()
        if self.request.method == 'POST':
            form = BreweryForm(self.request.POST)
            if form.validate():
                brewery = Brewery(key_name=key(*[user.user_id(), form.name.data]))
                brewery.user = user
                brewery.name = form.name.data
                brewery.description = form.description
