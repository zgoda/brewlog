# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from webapp2_extras.i18n import gettext

from handlers.base import BaseRequestHandler
from models.base import Brewery
from models.simple import Batch
from forms.brewery import BreweryForm


class BreweryHandler(BaseRequestHandler):

    def list_breweries(self):
        if self.logged_in:
            bl, cursor, more = Brewery.get_for_user(self.current_user)
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
                self.session.add_flash(gettext('brewery %s created') % brewery.name)
                next = self.request.GET.get('next', 'brewery-all')
                return self.redirect(self.uri_for(next))
        ctx = {
            'form': form,
        }
        self.render('brewery/form.html', ctx)

    def brewery_details(self, keyid):
        key = db.Key(urlsafe=keyid)
        brewery = key.get()
        if brewery is None:
            self.abort(404)
        form = None
        if brewery.owner != self.current_user:
            if self.request.method == 'POST':
                self.abort(403)
        else:
            form = BreweryForm(obj=brewery)
        if self.request.POST:
            form = BreweryForm(self.request.POST)
            if form.validate():
                brewery = form.save(user=self.current_user, obj=brewery)
                self.session.add_flash(gettext('data for brewery %s updated') % brewery.name)
                next = self.request.GET.get('next')
                if next is None:
                    next = self.uri_for('brewery-details', keyid=brewery.key.urlsafe())
                else:
                    next = self.uri_for(next)
                return self.redirect(next)
        latest_brews, brews_cursor, has_more_brews = Batch.get_for_brewery(brewery)
        ctx = {
            'brewery': brewery,
            'form': form,
            'latest_brews': latest_brews,
            'brews_cursor': brews_cursor,
            'has_more_brews': has_more_brews,
        }
        self.render('brewery/details.html', ctx)
