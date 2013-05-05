# -*- coding: utf-8 -*-

import wtforms as wf
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import DataRequired, Optional
from flaskext.babel import lazy_gettext as _

from brewlog import session
from brewlog.forms.base import BaseForm, BaseSubform
from brewlog.forms.widgets import SubformTableWidget
from brewlog.brewing import choices
from brewlog.brewing.models import Brew


class TastingNoteForm(BaseForm):
    date = DateField(_('date'))
    text = wf.TextAreaField(_('text'))


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
    fermentables = wf.TextAreaField(_('fermentables'), validators=[Optional()])
    hops = wf.TextAreaField(_('hop items'), validators=[Optional()])
    yeasts = wf.TextAreaField(_('yeast items'), validators=[Optional()])
    miscellany = wf.TextAreaField(_('miscellaneous items'), validators=[Optional()])
    mash_schedule = wf.TextAreaField(_('mash schedule'), validators=[Optional()])
    hopping_schedule = wf.TextAreaField(_('hopping schedule'), validators=[Optional()])
    additional_fermentation_steps = wf.TextAreaField(_('additional fermentation steps'), validators=[Optional()])
    is_public = wf.BooleanField(_('public'))
    is_draft = wf.BooleanField(_('draft'))

    def save(self, obj=None, save=True):
        if obj is None:
            obj = Brew()
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
