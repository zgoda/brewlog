# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from webapp2_extras.i18n import lazy_gettext as _

from handlers.base import BaseRequestHandler
from models.base import Brewery, BrewerProfile
from forms.account import ProfileForm


class ProfileHandler(BaseRequestHandler):

    def my_profile(self):
        if not (self.current_user or self.logged_in):
            return self.redirect(self.uri_for('auth-select-provider'))
        if self.request.method == 'POST':
            form = ProfileForm(self.request.POST)
            if form.validate():
                form.save(obj=self.brewer_profile, user=self.current_user)
                self.session.add_flash(_("your brewer's profile has been updated"))
                return self.redirect(self.uri_for('profile'))
        else:
            form = ProfileForm(obj=self.brewer_profile)
        bl, cursor, more = Brewery.get_for_user(self.current_user)
        ctx = {
            'profile': self.brewer_profile,
            'form': form,
            'breweries': bl,
            'cursor': cursor,
            'has_more': more,
        }
        self.render('account/profile.html', ctx)

    def view_details(self, keyid):
        key = db.Key(urlsafe=keyid)
        profile = key.get()
        if profile is None:
            self.abort(404)
        if self.current_user:
            current_profile = BrewerProfile.get_for_user(self.current_user)
            if current_profile:
                is_public = key != current_profile.key
            else:
                is_public = True
        else:
            is_public = True
        ctx = {
            'profile': profile,
            'is_public': is_public,
        }
        self.render('brewer/profile.html', ctx)
