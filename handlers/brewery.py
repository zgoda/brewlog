# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from handlers.base import BaseRequestHandler
from models.base import Brewery
from forms.brewery import BreweryForm


class BreweryHandler(BaseRequestHandler):

    def list_breweries(self):
        if self.logged_in:
            bl = Brewery.query(ancestor=self.current_user.key).fetch(20)
        else:
            bl = []
        ctx = {
            'breweries': bl,
            'user': self.current_user,
        }
        self.render('brewery/list.html', ctx)

    def add_brewery(self):
        form = BreweryForm(self.request.POST)
        if self.request.POST:
            import pdb; pdb.set_trace()
            if form.validate():
                form.save(user=self.current_user)
                return self.redirect(self.uri_for('brewery-main'))
        ctx = {
            'form': form,
        }
        self.render('brewery/form.html', ctx)

    def brewery_details(self, keyid):
        key = db.Key(urlsafe=keyid)
        brewery = key.get()
        if brewery is None:
            self.abort(404)
        ctx = {
            'brewery': brewery,
        }
        self.render('brewery/details.html', ctx)
