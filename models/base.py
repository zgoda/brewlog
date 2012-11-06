# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db
from webapp2 import uri_for
from webapp2_extras.appengine.auth.models import User

import markdown


class BrewerProfile(db.Model):
    user = db.KeyProperty(kind=User)
    first_name = db.TextProperty()
    last_name = db.TextProperty()
    nick = db.StringProperty()
    email = db.StringProperty()
    full_name = db.StringProperty()
    location = db.StringProperty()
    about_me = db.TextProperty()

    def get_absolute_url(self):
        return uri_for('profile-details', keyid=self.key.urlsafe())

    @classmethod
    def get_for_user(cls, user):
        pass


class Brewery(db.Model):
    user = db.KeyProperty(kind=User)
    name = db.StringProperty()
    description = db.TextProperty()
    description_html = db.TextProperty()
    established_date = db.DateProperty()

    def get_absolute_url(self):
        return uri_for('brewery-details', keyid=self.key.urlsafe())

    def _pre_put_hook(self):
        self.description_html = markdown.markdown(self.description, safe_mode='remove')
