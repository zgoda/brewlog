# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf
from wtforms.validators import DataRequired, Optional
from webapp2_extras.i18n import lazy_gettext as _

from forms.base import BaseForm
from models import choices
from models.simple import Batch, FermentableItem, HopItem, YeastItem, MiscItem, MashStep, HoppingStep, AdditionalFermentationStep, TastingNote


class FermentableItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    amount = wf.FloatField(_('amount'), validators=[DataRequired()])
    unit = wf.TextField(_('unit'), validators=[DataRequired()])
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = FermentableItem


class HopItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    year = wf.IntegerField(_('year'), validators=[Optional()])
    aa_content = wf.FloatField(_('alpha acids content'), validators=[Optional()])
    amount = wf.FloatField(_('amount'), validators=[DataRequired()])
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = HopItem


class YeastItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    code = wf.TextField(_('code'),
        description=_('manufacturer code for this strain'),
        validators=[Optional()])
    manufacturer = wf.TextAreaField(_('manufacturer'))
    use = wf.SelectField(_('usage'), choices=choices.YEAST_USE_CHOICES,
        description=_('select how this yeast was introduced into your brew'))
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = YeastItem


class MiscItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    amount = wf.FloatField(_('amount'), validators=[DataRequired()])
    unit = wf.TextField(_('unit'), validators=[DataRequired()])
    use = wf.SelectField(_('usage'), choices=choices.MISC_USE_CHOICES)
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = MiscItem


class MashStepForm(wf.Form):
    order = wf.IntegerField(_('order'))
    name = wf.TextField(_('name'), validators=[DataRequired()])
    temperature = wf.IntegerField(_('temperature'), validators=[DataRequired()])
    time = wf.IntegerField(_('time'), validators=[DataRequired()])
    step_type = wf.SelectField(_('step type'), choices=choices.STEP_TYPE_CHOICES)
    amount = wf.IntegerField(_('amount'),
        description=_('amount of water added as an infusion or mash drawn for decoction'),
        validators=[Optional()])
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = MashStep


class HoppingStepForm(wf.Form):
    addition_type = wf.SelectField(_('addition type'), choices=choices.HOPSTEP_TYPE_CHOICES)
    time = wf.IntegerField(_('time'), validators=[Optional()])
    variety = wf.TextField(_('variety'), validators=[DataRequired()])
    amount = wf.IntegerField(_('amount'), validators=[DataRequired()])
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = HoppingStep


class AdditionalFermentationStepForm(wf.Form):
    date = wf.DateField(_('date'), validators=[DataRequired()])
    amount = wf.FloatField(_('amount'), validators=[Optional()])
    og = wf.FloatField(_('original gravity'), validators=[Optional()])
    fg = wf.FloatField(_('final gravity'), validators=[Optional()])
    fermentation_temperature = wf.IntegerField(_('fermentation temperature'), validators=[Optional()])
    remarks = wf.TextAreaField(_('remarks'), validators=[Optional()])

    _model_class = AdditionalFermentationStep


class TastingNoteForm(wf.Form):
    date = wf.DateField(_('date'), validators=[DataRequired()])
    text = wf.TextAreaField(_('text'), validators=[DataRequired()])

    _model_class = TastingNote


class BrewForm(BaseForm):
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
    fermentables = wf.FieldList(wf.FormField(FermentableItemForm, _('fermentable items')), min_entries=1)
    hops = wf.FieldList(wf.FormField(HopItemForm, _('hop items')), min_entries=1)
    yeasts = wf.FieldList(wf.FormField(YeastItemForm, _('yeast items')), min_entries=1)
    miscellany = wf.FieldList(wf.FormField(MiscItemForm, _('miscellaneous items')), min_entries=1)
    mash_schedule = wf.FieldList(wf.FormField(MashStepForm, _('mash schedule')), min_entries=1)
    hopping_schedule = wf.FieldList(wf.FormField(HoppingStepForm, _('hopping schedule')), min_entries=1)
    additional_fermentation_steps = wf.FieldList(wf.FormField(AdditionalFermentationStepForm, _('additional fermentation steps')), min_entries=1)
    tasting_notes = wf.FieldList(wf.FormField(TastingNoteForm, _('tasting notes')), min_entries=1)
    is_public = wf.BooleanField(_('public'))
    is_draft = wf.BooleanField(_('draft'))

    def save(self, user, obj=None):
        if obj is None:
            obj = Batch(parent=user.key)
        kw = {
            'fermentables': [],
        }
        for field_name, field in self._fields.items():
            if field.type == 'FieldList':
                for entry in field.entries:
                    item = entry.form_class._model_class(name=entry.name.data, amount=entry.amount.data, unit=entry.unit.data, remarks=entry.remarks.data)
                    kw[field_name].append(item)
            else:
                kw[field_name] = field.data
        for k, v in kw:
            setattr(obj, k, v)
        obj.put()
        return obj
