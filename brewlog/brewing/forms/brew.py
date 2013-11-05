import wtforms as wf
from wtforms.fields.html5 import DateField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask.ext.babel import lazy_gettext as _
from flask.ext.login import current_user

from brewlog.db import session as dbsession
from brewlog.forms.base import BaseForm
from brewlog.forms.widgets import textarea_with_hints
from brewlog.forms.fields import TextAreaWithHintsField
from brewlog.brewing import choices
from brewlog.models.brewing import Brew, Brewery, FermentationStep


class FermentationStepForm(BaseForm):
    date = DateField(_('date'))
    name = wf.TextField(_('name'), validators=[DataRequired()])
    og = DecimalField(_('original gravity'))
    fg = DecimalField(_('final gravity'))
    amount = DecimalField(_('amount collected'))
    is_last = wf.BooleanField(_('last fermentation step'))
    notes = wf.TextAreaField(_('notes'), validators=[Optional()])

    def save(self, brew, obj=None):
        if obj is None:
            obj = FermentationStep(brew=brew)
        return super(FermentationStepForm, self).save(obj)


def user_breweries_query():
    return Brewery.query.filter_by(brewer=current_user).order_by(Brewery.name)


class BrewForm(BaseForm):
    brewery = QuerySelectField(_('brewery'), query_factory=user_breweries_query, get_label='name')
    name = wf.TextField(_('name'), validators=[DataRequired()])
    code = wf.TextField(_('code'), validators=[Optional()])
    style = wf.TextField(_('style'),
        description=_('descriptive name of style, as you see it'),
        validators=[Optional()])
    bjcp_style_code = wf.TextField(_('BJCP style code'), validators=[Optional()])
    bjcp_style_name = wf.TextField(_('BJCP style name'), validators=[Optional()])
    notes = wf.TextAreaField(_('notes'), validators=[Optional()])
    date_brewed = DateField(_('date brewed'), validators=[Optional()])
    fermentables = wf.TextAreaField(_('fermentables'), validators=[Optional()],
        description=_('put each fermentable on separate line to make nice list'))
    hops = wf.TextAreaField(_('hop items'), validators=[Optional()],
        description=_('put each hop item on separate line to make nice list'))
    yeast = wf.TextAreaField(_('yeast items'), validators=[Optional()],
        description=_('put each yeast item on separate line to make nice list'))
    misc = wf.TextAreaField(_('miscellaneous items'), validators=[Optional()],
        description=_('put each miscellanea on separare line to make nice list'))
    mash_steps = TextAreaWithHintsField(_('mash schedule'), validators=[Optional()],
        description=_('put each step on separate line to make nice list'),
        widget=textarea_with_hints)
    sparging = wf.TextField(_('sparging'), validators=[Optional()])
    hopping_steps = wf.TextAreaField(_('hopping schedule'), validators=[Optional()],
        description=_('put each step on separate line to make nice list'))
    boil_time = IntegerField(_('boil time'), validators=[Optional()])
    fermentation_start_date = DateField(_('fermentation start date'), validators=[Optional()])
    og = DecimalField(_('original gravity'), places=1, validators=[Optional()])
    fg = DecimalField(_('final gravity'), places=1, validators=[Optional()])
    brew_length = DecimalField(_('brew length'), places=1,
        description=_('total volume in fermenter (including yeast starter volume, if any)'),
        validators=[Optional()])
    fermentation_temperature = IntegerField(_('fermentation temperature'), validators=[Optional()])
    final_amount = DecimalField(_('final amount'), places=1,
        description=_('volume into bottling'), validators=[Optional()])
    bottling_date = DateField(_('bottling date'), validators=[Optional()])
    carbonation_type = wf.SelectField(_('type of carbonation'), choices=choices.CARBONATION_CHOICES,
        validators=[Optional()])
    carbonation_level = wf.SelectField(_('carbonation level'), choices=choices.CARB_LEVEL_CHOICES,
        validators=[Optional()])
    carbonation_used = wf.TextAreaField(_('carbonation used'), validators=[Optional()])
    is_public = wf.BooleanField(_('public'), default=True)
    is_draft = wf.BooleanField(_('draft'), default=False)

    def save(self, obj=None, save=True):
        if obj is None:
            obj = Brew()
        brew = super(BrewForm, self).save(obj, save=False)
        if save:
            dbsession.add(brew)
            fs = brew.fermentation_step_from_data()
            if fs:
                dbsession.add(fs)
            dbsession.commit()
        return brew
