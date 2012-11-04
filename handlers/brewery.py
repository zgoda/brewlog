# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from handlers.base import BaseRequestHandler
from models.base import Brewery
from forms.brewery import BreweryForm


class BreweryHandler(BaseRequestHandler):

    def list_breweries(self):
        if self.logged_in:
            bl, cursor, more = Brewery.query(ancestor=self.current_user.key).fetch_page(20)
        else:
            bl, cursor, more = [], None, False
        ctx = {
            'breweries': bl,
            'cursor': cursor,
            'has_more': more,
        }
        self.render('brewery/list.html', ctx)

    def all_breweries(self):
        bl, cursor, more = Brewery.query().fetch_page(20)
        ctx = {
            'breweries': bl,
            'cursor': cursor,
            'has_more': more,
        }
        self.render('brewery/list.html', ctx)

    def add_brewery(self):
        form = BreweryForm(self.request.POST)
        if self.request.POST:
            if form.validate():
                brewery = form.save(user=self.current_user)
                self.session.add_flash('brewery %s created' % brewery.name)
                return self.redirect(self.uri_for('brewery-all'))
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
