# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.ext import ndb as db
from webapp2 import uri_for

import markdown

from models.base import Brewery
from models import choices


class FermentableItem(db.Model):
    name = db.StringProperty()
    amount = db.IntegerProperty()
    unit = db.TextProperty()


class HopItem(db.Model):
    name = db.StringProperty()
    year = db.IntegerProperty()
    aa_content = db.FloatProperty()
    amount = db.IntegerProperty()


class YeastItem(db.Model):
    name = db.StringProperty()
    code = db.StringProperty()
    manufacturer = db.TextProperty()
    use = db.TextProperty(choices=choices.YEAST_USE_KEYS)


class MiscItem(db.Model):
    name = db.StringProperty()
    amount = db.IntegerProperty()
    unit = db.TextProperty()
    use = db.TextProperty(choices=choices.MISC_USE_KEYS)


class MashStep(db.Model):
    order = db.IntegerProperty()
    name = db.TextProperty()
    temperature = db.IntegerProperty()
    time = db.IntegerProperty()
    step_type = db.TextProperty(choices=choices.STEP_TYPE_KEYS)
    amount = db.IntegerProperty()


class HoppingStep(db.Model):
    addition_type = db.TextProperty(choices=choices.HOPSTEP_TYPE_KEYS)
    time = db.IntegerProperty()
    variety = db.StringProperty()
    amount = db.IntegerProperty()


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

    def _pre_put_hook(self):
        self.text_html = markdown.markdown(self.text, safe_mode='remove')


class Batch(db.Model):
    brewery = db.KeyProperty(kind=Brewery)
    created_at = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty()
    style = db.TextProperty()
    bjcp_style_code = db.StringProperty()
    bjcp_style_name = db.StringProperty()
    bjcp_style = db.TextProperty()
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
    carbonation_type = db.TextProperty(choices=choices.CARBONATION_KEYS)
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
    # recipe metadata
    is_public = db.BooleanProperty(default=True)
    is_draft = db.BooleanProperty(default=False)

    def get_absolute_url(self):
        return uri_for('brew-details', keyid=self.key.urlsafe())

    @property
    def user(self):
        owner_key = self.key.parent()
        return owner_key.get()

    def _pre_put_hook(self):
        self.notes_html = markdown.markdown(self.notes, safe_mode='remove')
        if self.bjcp_style_code and self.bjcp_style_name:
            self.bjcp_style = u'%s %s' % (self.bjcp_style_code, self.bjcp_style_name)
        if self.bjcp_style and not self.style:
            self.style = self.bjcp_style

    @classmethod
    def get_for_brewery(cls, brewery, limit=20):
        return cls.query(cls.brewery==brewery.key).order(-Batch.date_brewed).fetch_page(limit)
