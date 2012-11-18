# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf
from wtforms.validators import DataRequired
from webapp2_extras.i18n import lazy_gettext as _

from forms.base import BaseForm
from models import choices
from models.simple import Batch


class FermentableItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    amount = wf.FloatField(_('amount'), validators=[DataRequired()])
    unit = wf.TextField(_('unit'), validators=[DataRequired()])
    remarks = wf.TextAreaField(_('remarks'))


class HopItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    year = wf.IntegerField(_('year'))
    aa_content = wf.FloatField(_('alpha acids content'))
    amount = wf.FloatField(_('amount'), validators=[DataRequired()])
    remarks = wf.TextAreaField(_('remarks'))


class YeastItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    code = wf.TextField(_('code'))
    manufacturer = wf.TextAreaField(_('manufacturer'))
    use = wf.SelectField(_('usage'), choices=choices.YEAST_USE_CHOICES)
    remarks = wf.TextAreaField(_('remarks'))


class MiscItemForm(wf.Form):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    amount = wf.FloatField(_('amount'), validators=[DataRequired()])
    unit = wf.TextField(_('unit'), validators=[DataRequired()])
    use = wf.SelectField(_('usage'), choices=choices.MISC_USE_CHOICES)
    remarks = wf.TextAreaField(_('remarks'))


class MashStepForm(wf.Form):
    order = wf.IntegerField(_('order'))
    name = wf.TextField(_('name'), validators=[DataRequired()])
    temperature = wf.IntegerField(_('temperature'), validators=[DataRequired()])
    time = wf.IntegerField(_('time'), validators=[DataRequired()])
    step_type = wf.SelectField(_('step type'), choices=choices.STEP_TYPE_CHOICES)
    amount = wf.IntegerField(_('amount'))
    remarks = wf.TextAreaField(_('remarks'))


class HoppingStepForm(wf.Form):
    addition_type = wf.SelectField(_('addition type'), choices=choices.HOPSTEP_TYPE_CHOICES)
    time = wf.IntegerField(_('time'))
    variety = wf.TextField(_('variety'))
    amount = wf.IntegerField(_('amount'))
    remarks = wf.TextAreaField(_('remarks'))


class AdditionalFermentationStepForm(wf.Form):
    date = wf.DateField(_('date'), validators=[DataRequired()])
    amount = wf.FloatField(_('amount'))
    og = wf.FloatField(_('original gravity'))
    fg = wf.FloatField(_('final gravity'))
    fermentation_temperature = wf.IntegerField(_('fermentation temperature'))
    remarks = wf.TextAreaField(_('remarks'))


class TastingNoteForm(wf.Form):
    date = wf.DateField(_('date'), validators=[DataRequired()])
    text = wf.TextAreaField(_('text'), validators=[DataRequired()])


class BrewForm(BaseForm):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    style = wf.TextField(_('style'))
    bjcp_style_code = wf.TextField(_('BJCP style code'))
    bjcp_style_name = wf.TextField(_('BJCP style name'))
    date_brewed = wf.DateField(_('date brewed'))
    notes = wf.TextAreaField(_('notes'))
    boil_time = wf.IntegerField(_('boil time'))
    fermentation_start_date = wf.DateField(_('fermentation start date'))
    og = wf.FloatField(_('original gravity'))
    fg = wf.FloatField(_('final gravity'))
    brew_length = wf.FloatField(_('brew length'))
    fermentation_temperature = wf.IntegerField(_('fermentation temperature'))
    final_amount = wf.FloatField(_('final amount'))
    bottling_date = wf.DateField(_('bottling date'))
    carbonation_type = wf.SelectField(_('type of carbonation'), choices=choices.CARBONATION_CHOICES)
    fermentables = wf.FieldList(wf.FormField(FermentableItemForm), _('fermentable item'), min_entries=1)
    hops = wf.FieldList(wf.FormField(HopItemForm), _('hop item'), min_entries=1)
    yeasts = wf.FieldList(wf.FormField(YeastItemForm), _('yeast item'), min_entries=1)
    miscellany = wf.FieldList(wf.FormField(MiscItemForm), _('miscellaneous item'))
    mash_schedule = wf.FieldList(wf.FormField(MashStepForm), _('mash schedule item'), min_entries=1)
    hopping_schedule = wf.FieldList(wf.FormField(HoppingStepForm), _('hopping schedule item'), min_entries=1)
    additional_fermentation_steps = wf.FieldList(wf.FormField(AdditionalFermentationStepForm), _('additional fermentation step'))
    tasting_notes = wf.FieldList(wf.FormField(TastingNoteForm), _('tasting note'))
    is_public = wf.BooleanField(_('public'))
    is_draft = wf.BooleanField(_('draft'))

    def save(self, user, obj=None):
        if obj is None:
            obj = Batch(parent=user.key)
        return super(BrewForm, self).save(user, obj, save=True)
