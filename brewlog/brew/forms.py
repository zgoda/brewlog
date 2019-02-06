import wtforms as wf
from flask_babel import lazy_gettext as _
from flask_login import current_user
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import DataRequired
from wtforms_alchemy import QuerySelectField

from ..forms.base import BaseForm, BaseObjectForm
from ..forms.fields import TextAreaWithHintsField
from ..forms.widgets import textarea_with_hints
from ..models import choices
from ..models.brewing import Brew, Brewery, FermentationStep


class FermentationStepForm(BaseObjectForm):
    date = DateField(_('date'), validators=[DataRequired()])
    name = wf.StringField(_('name'), validators=[DataRequired()])
    og = DecimalField(_('original gravity'), places=1)
    fg = DecimalField(_('final gravity'), places=1)
    temperature = wf.IntegerField(_('temperature'))
    volume = DecimalField(_('volume collected'), places=1)
    notes = wf.TextAreaField(_('notes'))

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = FermentationStep(brew=brew)
        return super(FermentationStepForm, self).save(obj, save)


def user_breweries_query():
    return Brewery.query.filter_by(brewer=current_user).order_by(Brewery.name)


class BrewForm(BaseObjectForm):
    brewery = QuerySelectField(
        _('brewery'), query_factory=user_breweries_query, get_label='name',
        validators=[DataRequired()]
    )
    name = wf.StringField(_('name'), validators=[DataRequired()])
    code = wf.StringField(_('code'))
    style = wf.StringField(
        _('style'),
        description=_('descriptive name of style, as you see it'),
    )
    bjcp_style_code = wf.StringField(_('BJCP style code'))
    bjcp_style_name = wf.StringField(_('BJCP style name'))
    notes = wf.TextAreaField(_('notes'))
    date_brewed = DateField(_('date brewed'))
    fermentables = wf.TextAreaField(
        _('fermentables'),
        description=_('put each fermentable on separate line to make nice list')
    )
    hops = wf.TextAreaField(
        _('hop items'),
        description=_('put each hop item on separate line to make nice list')
    )
    yeast = wf.TextAreaField(
        _('yeast items'),
        description=_('put each yeast item on separate line to make nice list')
    )
    misc = wf.TextAreaField(
        _('miscellaneous items'),
        description=_('put each miscellanea on separare line to make nice list')
    )
    mash_steps = TextAreaWithHintsField(
        _('mash schedule'),
        description=_('put each step on separate line to make nice list'),
        widget=textarea_with_hints
    )
    sparging = wf.StringField(_('sparging'))
    hopping_steps = wf.TextAreaField(
        _('hopping schedule'),
        description=_('put each step on separate line to make nice list')
    )
    boil_time = IntegerField(_('boil time'))
    final_amount = DecimalField(
        _('final amount'), places=1,
        description=_('volume into bottling')
    )
    bottling_date = DateField(_('bottling date'))
    carbonation_type = wf.SelectField(
        _('type of carbonation'), choices=choices.CARBONATION_CHOICES
    )
    carbonation_level = wf.SelectField(
        _('carbonation level'), choices=choices.CARB_LEVEL_CHOICES
    )
    carbonation_used = wf.TextAreaField(_('carbonation used'))
    is_public = wf.BooleanField(_('public'), default=True)
    is_draft = wf.BooleanField(_('draft'), default=False)

    def save(self, obj=None, save=True):
        if obj is None:
            obj = Brew()
        return super(BrewForm, self).save(obj, save)


class ChangeStateForm(BaseForm):
    action = wf.RadioField(_('action'), choices=choices.ACTION_CHOICES, default='available')
