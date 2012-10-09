# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import db


class Brewery(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    description = db.TextProperty()


class FermentableItem(db.Model):
    name = db.StringProperty()
    amount = db.IntegerProperty()
    unit = db.TextProperty()
    batch = db.ReferenceProperty(Batch, collection_name='fermentables')
    remarks = db.TextProperty()


class HopItem(db.Model):
    name = db.StringProperty()
    year = db.IntegetProperty()
    aa_content = db.FloatProperty()
    amount = db.IntegerProperty()
    batch = db.ReferenceProperty(Batch, collection_name='hops')
    remarks = db.TextProperty()


class YeastItem(db.Model):
    name = db.StringProperty()
    code = db.StringProperty()
    manufacturer = db.TextProperty()
    use = db.TextProperty(choices=('primary', 'secondary', 'bottling'))
    batch = db.ReferenceProperty(Batch, collection_name='yeast')
    remarks = db.TextProperty()


class MiscItem(db.Model):
    name = db.StringProperty()
    amount = db.IntegerProperty()
    unit = db.TextProperty()
    use = db.TextProperty(choices=('mash', 'boil', 'fermentation', 'bottling'))
    batch = db.ReferenceProperty(Batch, collection_name='misc')
    remarks = db.TextProperty()


class MashStep(db.Model):
    batch = db.ReferenceProperty(Batch, collection_name='mash_steps')
    order = db.IntegerProperty()
    name = db.TextProperty()
    temperature = db.IntegerProperty()
    time = db.IntegerProperty()
    step_type = db.TextProperty(choices=('infusion', 'decoction', 'temperature'))
    amount = db.IntegerProperty()
    remarks = db.TextProperty()


class HoppingStep(db.Model):
    addition_type = db.TextProperty(choices=('mash', 'first wort', 'boil', 'post-boil', 'dry hop'))
    time = db.IntegerProperty()
    variety = db.StringProperty()
    amount = db.IntegerProperty()
    batch = db.ReferenceProperty(Batch, collection_name='hopping_steps')
    remarks = db.TextProperty()


class Batch(db.Model):
    brewery = db.ReferenceProperty(Brewery, collection_name='batches')
    date_brewed = db.DateProperty()
    notes = db.TextProperty()
    boil_time = db.IntegerProperty()
    fermentation_start_date = db.DateProperty()
    og = db.FloatProperty()
    fg = db.FloatProperty()
    brew_length = db.FloatProperty()
    fermentation_temperature = db.IntegerProperty()

