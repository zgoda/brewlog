# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from handlers.base import BaseRequestHandler
from forms.account import ProfileForm
from models.base import BrewerProfile
from utils.decorators.auth import simpleauth_login_required


class ProfileHandler(BaseRequestHandler):

    @simpleauth_login_required
    def get(self):
        try:
            profile = BrewerProfile.query(ancestor=self.current_user.key).fetch(1)[0]
        except IndexError:
            profile = None
        ctx = {
            'profile': profile,
        }
        self.render('account/profile.html', ctx)

    def view_details(self, keyid):
        key = db.Key(urlsafe=keyid)
        profile = key.get()
        if profile is None:
            self.abort(404)
        ctx = {
            'profile': profile,
        }
        self.render('brewer/profile.html', ctx)
