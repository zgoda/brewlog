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
    def get_or_create_for_user(cls, user, save=True):
        try:
            return cls.query(user==user.key, ancestor=user).fetch(1)[0]
        except IndexError:
            profile = cls(parent=user, user=user.key)
            if save:
                profile.put()
            return profile


class Brewery(db.Model):
    user = db.KeyProperty(kind=User)
    name = db.StringProperty()
    description = db.TextProperty()
    description_html = db.TextProperty()
    established_date = db.DateProperty()
    # alternative established date
    est_year = db.IntegerProperty()
    est_month = db.IntegerProperty()
    est_day = db.IntegerProperty

    def get_absolute_url(self):
        return uri_for('brewery-details', keyid=self.key.urlsafe())

    def _pre_put_hook(self):
        self.description_html = markdown.markdown(self.description, safe_mode='remove')
        if self.established_date is not None:
            self.est_year = self.established_date.year
            self.est_month = self.established_date.month
            self.est_day = self.established_date.day

    def get_or_create_for_user(cls, user, save=True):
        result = cls.query(user=user.key, ancestor=user).fetch_page(20)
        if not result:
            brewery = cls(parent=user, user=user.key)
            if save:
                brewery.put()
            result = [brewery]
        return result
