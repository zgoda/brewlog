# -*- coding: utf-8 -*-

import wtforms as wf
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import DataRequired, Optional
from flaskext.babel import lazy_gettext as _

from brewlog import session
from brewlog.forms.base import BaseForm, BaseSubform
from brewlog.forms.widgets import SubformTableWidget
from brewlog.brewing import choices
from brewlog.brewing.models import Brew, Fermentable, Hop, Yeast, Misc, MashStep, HoppingStep, AdditionalFermentationStep, TastingNote


class FermentableItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    amount = wf.FloatField(_('amount'))
    unit = wf.TextField(_('unit'))

    _model_class = Fermentable
    _required = ('name', 'amount', 'unit')


class HopItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    year = IntegerField(_('year'))
    aa_content = wf.FloatField(_('alpha acids content'))
    amount = wf.FloatField(_('amount'))

    _model_class = Hop
    _required = ('name', 'amount')


class YeastItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    code = wf.TextField(_('code'),
        description=_('manufacturer code for this strain'))
    manufacturer = wf.TextAreaField(_('manufacturer'))
    use = wf.SelectField(_('usage'), choices=choices.YEAST_USE_CHOICES,
        description=_('select how this yeast was introduced into your brew'))

    _model_class = Yeast
    _required = ('name', 'manufacturer', 'use')


class MiscItemForm(BaseSubform):
    name = wf.TextField(_('name'))
    amount = wf.FloatField(_('amount'))
    unit = wf.TextField(_('unit'))
    use = wf.SelectField(_('usage'), choices=choices.MISC_USE_CHOICES)

    _model_class = Misc
    _required = ('name', 'amount', 'unit', 'use')


class MashStepForm(BaseSubform):
    order = IntegerField(_('order'))
    name = wf.TextField(_('name'))
    temperature = IntegerField(_('temperature'))
    time = IntegerField(_('time'))
    step_type = wf.SelectField(_('step type'), choices=choices.STEP_TYPE_CHOICES)
    amount = wf.IntegerField(_('amount'),
        description=_('amount of water added as an infusion or mash drawn for decoction'))

    _model_class = MashStep
    _required = ('temperature', 'time', 'step_type')


class HoppingStepForm(BaseSubform):
    addition_type = wf.SelectField(_('addition type'), choices=choices.HOPSTEP_TYPE_CHOICES)
    time = IntegerField(_('time'))
    variety = wf.TextField(_('variety'))
    amount = wf.IntegerField(_('amount'))

    _model_class = HoppingStep
    _required = ('addition_type', 'time', 'variety', 'amount')


class AdditionalFermentationStepForm(BaseSubform):
    date = DateField(_('date'))
    amount = wf.FloatField(_('amount'))
    og = wf.FloatField(_('original gravity'))
    fg = wf.FloatField(_('final gravity'))
    fermentation_temperature = IntegerField(_('fermentation temperature'))

    _model_class = AdditionalFermentationStep
    _required = ('date', 'og')


class TastingNoteForm(BaseSubform):
    date = DateField(_('date'))
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
    date_brewed = DateField(_('date brewed'), validators=[Optional()])
    notes = wf.TextAreaField(_('notes'), validators=[Optional()])
    boil_time = IntegerField(_('boil time'), validators=[Optional()])
    fermentation_start_date = DateField(_('fermentation start date'), validators=[Optional()])
    og = wf.FloatField(_('original gravity'), validators=[Optional()])
    fg = wf.FloatField(_('final gravity'), validators=[Optional()])
    brew_length = wf.FloatField(_('brew length'),
        description=_('total volume in fermenter (including yeast starter volume, if any)'),
        validators=[Optional()])
    fermentation_temperature = IntegerField(_('fermentation temperature'), validators=[Optional()])
    final_amount = wf.FloatField(_('final amount'),
        description=_('volume into bottling'),
        validators=[Optional()])
    bottling_date = DateField(_('bottling date'), validators=[Optional()])
    carbonation_type = wf.SelectField(_('type of carbonation'), choices=choices.CARBONATION_CHOICES,
        validators=[Optional()])
    fermentables = wf.FieldList(wf.FormField(FermentableItemForm, _('fermentable items'), widget=SubformTableWidget()), min_entries=5,
        validators=[Optional()])
    hops = wf.FieldList(wf.FormField(HopItemForm, _('hop items'), widget=SubformTableWidget()), min_entries=5, validators=[Optional()])
    yeasts = wf.FieldList(wf.FormField(YeastItemForm, _('yeast items'), widget=SubformTableWidget()), min_entries=5, validators=[Optional()])
    miscellany = wf.FieldList(wf.FormField(MiscItemForm, _('miscellaneous items'), widget=SubformTableWidget()), min_entries=5,
        validators=[Optional()])
    mash_schedule = wf.FieldList(wf.FormField(MashStepForm, _('mash schedule'), widget=SubformTableWidget()), min_entries=5,
        validators=[Optional()])
    hopping_schedule = wf.FieldList(wf.FormField(HoppingStepForm, _('hopping schedule'), widget=SubformTableWidget()), min_entries=5,
        validators=[Optional()])
    additional_fermentation_steps = wf.FieldList(wf.FormField(AdditionalFermentationStepForm, _('additional fermentation steps'), widget=SubformTableWidget()),
        min_entries=5, validators=[Optional()])
    tasting_notes = wf.FieldList(wf.FormField(TastingNoteForm, _('tasting notes'), widget=SubformTableWidget()), min_entries=5,
        validators=[Optional()])
    is_public = wf.BooleanField(_('public'))
    is_draft = wf.BooleanField(_('draft'))

    def save(self, brewery, obj=None, save=True):
        if obj is None:
            obj = Brew(brewery=brewery)
        kw = {}
        for field_name, field in self._fields.items():
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
        if save:
            session.add(obj)
            session.commit()
        return obj
