# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db

from models.base import Brewery


class FermentableItem(db.Model):
    name = db.StringProperty()
    amount = db.IntegerProperty()
    unit = db.TextProperty()
    remarks = db.TextProperty()
    remarks_html = db.TextProperty()


class HopItem(db.Model):
    name = db.StringProperty()
    year = db.IntegerProperty()
    aa_content = db.FloatProperty()
    amount = db.IntegerProperty()
    remarks = db.TextProperty()
    remarks_html = db.TextProperty()


class YeastItem(db.Model):
    name = db.StringProperty()
    code = db.StringProperty()
    manufacturer = db.TextProperty()
    use = db.TextProperty(choices=('primary', 'secondary', 'bottling'))
    remarks = db.TextProperty()
    remarks_html = db.TextProperty()


class MiscItem(db.Model):
    name = db.StringProperty()
    amount = db.IntegerProperty()
    unit = db.TextProperty()
    use = db.TextProperty(choices=('mash', 'boil', 'fermentation', 'bottling'))
    remarks = db.TextProperty()
    remarks_html = db.TextProperty()


class MashStep(db.Model):
    order = db.IntegerProperty()
    name = db.TextProperty()
    temperature = db.IntegerProperty()
    time = db.IntegerProperty()
    step_type = db.TextProperty(choices=('infusion', 'decoction', 'temperature'))
    amount = db.IntegerProperty()
    remarks = db.TextProperty()
    remarks_html = db.TextProperty()


class HoppingStep(db.Model):
    addition_type = db.TextProperty(choices=('mash', 'first wort', 'boil', 'post-boil', 'dry hop'))
    time = db.IntegerProperty()
    variety = db.StringProperty()
    amount = db.IntegerProperty()
    remarks = db.TextProperty()
    remarks_html = db.TextProperty()


class AdditionalFermentationStep(db.Model):
    date = db.DateProperty()
    amount = db.FloatProperty()
    og = db.FloatProperty()
    fg = db.FloatProperty()
    fermentation_temperature = db.IntegerProperty()


class TastingNote(db.Model):
    date = db.DateProperty()
    text = db.TextProperty()
    text_html = db.TextProperty()


class Batch(db.Model):
    brewery = db.KeyProperty(kind=Brewery)
    date_brewed = db.DateProperty()
    notes = db.TextProperty()
    notes_html = db.TextProperty()
    boil_time = db.IntegerProperty()
    fermentation_start_date = db.DateProperty()
    og = db.FloatProperty()
    fg = db.FloatProperty()
    brew_length = db.FloatProperty()
    fermentation_temperature = db.IntegerProperty()
    final_amount = db.FloatProperty()
    bottling_date = db.DateProperty()
    carbonation_type = db.TextProperty(choices=('forced in keg', 'keg with priming', 'bottles with priming'))
    carbonation_used = db.TextProperty()
    # lists
    fermentables = db.LocalStructuredProperty(FermentableItem, repeated=True)
    hops = db.LocalStructuredProperty(HopItem, repeated=True)
    yeasts = db.LocalStructuredProperty(YeastItem, repeated=True)
    miscellany = db.LocalStructuredProperty(MiscItem, repeated=True)
    # processes
    mash_schedule = db.LocalStructuredProperty(MashStep, repeated=True)
    hopping_schedule = db.LocalStructuredProperty(HoppingStep, repeated=True)
    # fermentation
    additional_fermentation_steps = db.LocalStructuredProperty(AdditionalFermentationStep, repeated=True)
    # tasting notes
    tasting_notes = db.LocalStructuredProperty(TastingNote, repeated=True)