# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db
from webapp2 import uri_for
from webapp2_extras.appengine.auth.models import User

import markdown


class BrewerProfile(db.Model):
    first_name = db.TextProperty()
    last_name = db.TextProperty()
    nick = db.StringProperty()
    email = db.StringProperty()
    full_name = db.StringProperty()
    location = db.StringProperty()
    about_me = db.TextProperty()

    def get_absolute_url(self):
        return uri_for('profile-details', keyid=self.key.urlsafe())

    def _pre_put_hook(self):
        fn = self.first_name or u''
        ln = self.last_name or u''
        full_name = u'%s %s' % (fn, ln)
        self.full_name = full_name.strip()

    @classmethod
    def get_for_user(cls, user):
        try:
            return cls.query(ancestor=user.key).fetch(1)[0]
        except IndexError:
            return None


class Brewery(db.Model):
    name = db.StringProperty()
    description = db.TextProperty()
    description_html = db.TextProperty()
    established_date = db.DateProperty()
    # alternative established date
    est_year = db.IntegerProperty()
    est_month = db.IntegerProperty()
    est_day = db.IntegerProperty

    @property
    def owner(self):
        owner_key = self.key.parent()
        return owner_key.get()

    def get_absolute_url(self):
        return uri_for('brewery-details', keyid=self.key.urlsafe())

    def _pre_put_hook(self):
        self.description_html = markdown.markdown(self.description, safe_mode='remove')
        if self.established_date is not None:
            self.est_year = self.established_date.year
            self.est_month = self.established_date.month
            self.est_day = self.established_date.day

    @classmethod
    def get_for_user(cls, user):
        return cls.query(ancestor=user.key).order(Brewery.name).fetch_page(20)
