# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db


class Brewery(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    description = db.TextProperty()
    description_html = db.TextProperty()

    def get_absolute_url(self):
        return '/brewery/%s' % self.key()