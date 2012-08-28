#! -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import db


class Brewery(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()


class Batch(db.Model):
	brewery = db.ReferenceProperty(Brewery, collection_name='batches')
	date_brewed = db.DateProperty()