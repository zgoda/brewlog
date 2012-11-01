# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db
from webapp2_extras.appengine.auth.models import User


class BrewerProfile(db.Model):
    user = db.KeyProperty(kind=User)
    first_name = db.TextProperty()
    last_name = db.TextProperty()
    nick = db.StringProperty()
    full_name = db.StringProperty()
    location = db.StringProperty()
    about_me = db.TextProperty()


class Brewery(db.Model):
    user = db.KeyProperty(kind=User)
    name = db.StringProperty()
    description = db.TextProperty()
    description_html = db.TextProperty()
    established_date = db.DateProperty()

    def get_absolute_url(self):
        return '/brewery/%s' % self.key.urlsafe()
