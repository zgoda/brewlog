# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from webapp2_extras.i18n import lazy_gettext as _

from handlers.base import BaseRequestHandler
from forms.brew import BrewForm
from models.simple import Batch
from models.base import Brewery


class BrewHandler(BaseRequestHandler):

    def brew_list(self):
        brews = Batch.query(Batch.is_public==True).order(-Batch.created_at).fetch(10)
        ctx = {
            'brews': brews
        }
        self.render('brew/list.html', ctx)

    def add_brew(self):
        form = BrewForm(self.request.POST)
        form.brewery.choices = [(b.key.urlsafe(), b.name) for b in Brewery.get_for_user(self.current_user, limit=15)[0]]
        if self.request.POST:
            if form.validate():
                brew = form.save(user=self.current_user)
                self.session.add_flash(_('brew %s saved') % brew.name)
                next = self.uri_for('brew-details', keyid=brew.key.urlsafe())
                return self.redirect(next)
        ctx = {
            'form': form,
        }
        self.render('brew/form.html', ctx)

    def brew_details(self, keyid):
        key = db.Key(urlsafe=keyid)
        brew = key.get()
        if brew is None:
            self.abort(404)
        form = None
        brewery = brew.brewery.get()
        if brewery.owner != self.current_user:
            if self.request.method == 'POST':
                self.abort(403)
        else:
            if self.request.POST:
                form = BrewForm(self.request.POST)
                if form.validate():
                    brew = form.save(user=self.current_user, obj=brew)
                    self.session.add_flash(_('data for brew %s updated') % brew.name)
                    next = self.request.GET.get('next')
                    if next is None:
                        next = self.uri_for('brew-details', keyid=brew.key.urlsafe())
                    else:
                        next = self.uri_for(next)
                    return self.redirect(next)
            form = BrewForm(obj=brew)
            form.brewery.choices = [(b.key.urlsafe(), b.name) for b in Brewery.get_for_user(self.current_user, limit=15)[0]]
        latest_brews, brews_cursor, has_more_brews = Batch.get_for_brewery(brewery)
        ctx = {
            'brew': brew,
            'brewery': brewery,
            'form': form,
            'latest_brews': latest_brews,
            'brews_cursor': brews_cursor,
            'has_more_brews': has_more_brews,
        }
        self.render('brew/details.html', ctx)
