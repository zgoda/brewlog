# -*- coding: utf-8 -*-

__revision__ = '$Id$'


from google.appengine.ext import ndb as db

import wtforms as wf
from wtforms.validators import DataRequired, Optional
from webapp2_extras.i18n import lazy_gettext as _

from forms.base import BaseForm, BaseSubform
from models import choices
from models.simple import Batch, FermentableItem, HopItem, YeastItem, MiscItem, MashStep, HoppingStep, AdditionalFermentationStep, TastingNote


class FermentableItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    amount = wf.FloatField(_('amount'))
    unit = wf.TextField(_('unit'))
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = FermentableItem
    _required = ('name', 'amount', 'unit')


class HopItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    year = wf.IntegerField(_('year'))
    aa_content = wf.FloatField(_('alpha acids content'))
    amount = wf.FloatField(_('amount'))
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = HopItem
    _required = ('name', 'amount')


class YeastItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    code = wf.TextField(_('code'),
        description=_('manufacturer code for this strain'))
    manufacturer = wf.TextAreaField(_('manufacturer'))
    use = wf.SelectField(_('usage'), choices=choices.YEAST_USE_CHOICES,
        description=_('select how this yeast was introduced into your brew'))
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = YeastItem
    _required = ('name', 'manufacturer', 'use')


class MiscItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    amount = wf.FloatField(_('amount'))
    unit = wf.TextField(_('unit'))
    use = wf.SelectField(_('usage'), choices=choices.MISC_USE_CHOICES)
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = MiscItem
    _required = ('name', 'amount', 'unit', 'use')


class MashStepForm(BaseSubform):
    order = wf.IntegerField(_('order'))
    name = wf.TextField(_('name'))
    temperature = wf.IntegerField(_('temperature'))
    time = wf.IntegerField(_('time'))
    step_type = wf.SelectField(_('step type'), choices=choices.STEP_TYPE_CHOICES)
    amount = wf.IntegerField(_('amount'),
        description=_('amount of water added as an infusion or mash drawn for decoction'))
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = MashStep
    _required = ('temperature', 'time', 'step_type')


class HoppingStepForm(BaseSubform):
    addition_type = wf.SelectField(_('addition type'), choices=choices.HOPSTEP_TYPE_CHOICES)
    time = wf.IntegerField(_('time'))
    variety = wf.TextField(_('variety'))
    amount = wf.IntegerField(_('amount'))
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = HoppingStep
    _required = ('addition_type', 'time', 'variety', 'amount')


class AdditionalFermentationStepForm(BaseSubform):
    date = wf.DateField(_('date'))
    amount = wf.FloatField(_('amount'))
    og = wf.FloatField(_('original gravity'))
    fg = wf.FloatField(_('final gravity'))
    fermentation_temperature = wf.IntegerField(_('fermentation temperature'))
    remarks = wf.TextAreaField(_('remarks'))

    _model_class = AdditionalFermentationStep
    _required = ('date', 'og')


class TastingNoteForm(BaseSubform):
    date = wf.DateField(_('date'))
    text = wf.TextAreaField(_('text'))

    _model_class = TastingNote
    _required = ('date', 'text')


class BrewForm(BaseForm):
    brewery = wf.SelectField(_('brewery'), coerce=str)
    name = wf.TextField(_('name'), validators=[DataRequired()])
    style = wf.TextField(_('style'),
        description=_('descriptive name of style, as you see it'),
        validators=[Optional()])
    bjcp_style_code = wf.TextField(_('BJCP style code'), validators=[Optional()])
    bjcp_style_name = wf.TextField(_('BJCP style name'), validators=[Optional()])
    date_brewed = wf.DateField(_('date brewed'), validators=[Optional()])
    notes = wf.TextAreaField(_('notes'), validators=[Optional()])
    boil_time = wf.IntegerField(_('boil time'), validators=[Optional()])
    fermentation_start_date = wf.DateField(_('fermentation start date'), validators=[Optional()])
    og = wf.FloatField(_('original gravity'), validators=[Optional()])
    fg = wf.FloatField(_('final gravity'), validators=[Optional()])
    brew_length = wf.FloatField(_('brew length'),
        description=_('total volume in fermenter (including yeast starter volume, if any)'),
        validators=[Optional()])
    fermentation_temperature = wf.IntegerField(_('fermentation temperature'), validators=[Optional()])
    final_amount = wf.FloatField(_('final amount'),
        description=_('volume into bottling'),
        validators=[Optional()])
    bottling_date = wf.DateField(_('bottling date'), validators=[Optional()])
    carbonation_type = wf.SelectField(_('type of carbonation'), choices=choices.CARBONATION_CHOICES,
        validators=[Optional()])
    fermentables = wf.FieldList(wf.FormField(FermentableItemForm, _('fermentable items')), min_entries=1,
        validators=[Optional()])
    hops = wf.FieldList(wf.FormField(HopItemForm, _('hop items')), min_entries=1, validators=[Optional()])
    yeasts = wf.FieldList(wf.FormField(YeastItemForm, _('yeast items')), min_entries=1, validators=[Optional()])
    miscellany = wf.FieldList(wf.FormField(MiscItemForm, _('miscellaneous items')), min_entries=1,
        validators=[Optional()])
    mash_schedule = wf.FieldList(wf.FormField(MashStepForm, _('mash schedule')), min_entries=1,
        validators=[Optional()])
    hopping_schedule = wf.FieldList(wf.FormField(HoppingStepForm, _('hopping schedule')), min_entries=1,
        validators=[Optional()])
    additional_fermentation_steps = wf.FieldList(wf.FormField(AdditionalFermentationStepForm, _('additional fermentation steps')),
        min_entries=1, validators=[Optional()])
    tasting_notes = wf.FieldList(wf.FormField(TastingNoteForm, _('tasting notes')), min_entries=1,
        validators=[Optional()])
    is_public = wf.BooleanField(_('public'))
    is_draft = wf.BooleanField(_('draft'))

    def save(self, user, obj=None):
        if obj is None:
            obj = Batch(parent=user.key)
        kw = {}
        for field_name, field in self._fields.items():
            if field_name == 'brewery':
                kw[field_name] = db.Key(urlsafe=field.data)
            else:
                if field.type == 'FieldList':
                    items = kw.get(field_name, [])
                    for entry in field.entries:
                        item = entry.form.item_from_data()
                        if item:
                            items.append(item)
                    kw[field_name] = items
                else:
                    kw[field_name] = field.data
        for k, v in kw.items():
            setattr(obj, k, v)
        obj.put()
        return obj
