from flask_babel import lazy_gettext as _
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import BooleanField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import InputRequired, Optional

from ..forms.base import BaseForm, BaseObjectForm
from ..forms.fields import TextAreaWithHintsField
from ..forms.utils import Button
from ..forms.widgets import textarea_with_hints
from ..models import Brew, Brewery, choices


def user_breweries_query() -> BaseQuery:
    return Brewery.query.filter_by(brewer=current_user).order_by(Brewery.name)


class BrewForm(BaseObjectForm):
    brewery = QuerySelectField(
        _('brewery'), query_factory=user_breweries_query, get_label='name',
        validators=[InputRequired()]
    )
    name = StringField(_('name'), validators=[InputRequired()])
    code = StringField(_('code'))
    style = StringField(
        _('style'),
        description=_('descriptive name of style, as you see it'),
    )
    bjcp_style_code = StringField(_('BJCP style code'))
    bjcp_style_name = StringField(_('BJCP style name'))
    notes = TextAreaField(_('notes'))
    date_brewed = DateField(_('date brewed'), validators=[Optional()])
    fermentables = TextAreaField(
        _('fermentables'),
        description=_('put each fermentable on separate line to make nice list')
    )
    hops = TextAreaField(
        _('hop items'),
        description=_('put each hop item on separate line to make nice list')
    )
    yeast = TextAreaField(
        _('yeast items'),
        description=_('put each yeast item on separate line to make nice list')
    )
    misc = TextAreaField(
        _('miscellaneous items'),
        description=_('put each miscellanea on separare line to make nice list')
    )
    mash_steps = TextAreaWithHintsField(
        _('mash schedule'),
        description=_('put each step on separate line to make nice list'),
        widget=textarea_with_hints
    )
    sparging = StringField(_('sparging'))
    hopping_steps = TextAreaField(
        _('hopping schedule'),
        description=_('put each step on separate line to make nice list')
    )
    boil_time = IntegerField(_('boil time'), validators=[Optional()])
    final_amount = DecimalField(
        _('final amount'), places=1,
        description=_('volume into bottling'),
        validators=[Optional()]
    )
    bottling_date = DateField(_('bottling date'), validators=[Optional()])
    carbonation_type = SelectField(
        _('type of carbonation'), choices=choices.CARBONATION_CHOICES,
    )
    carbonation_level = SelectField(
        _('carbonation level'), choices=choices.CARB_LEVEL_CHOICES,
    )
    carbonation_used = TextAreaField(_('carbonation used'))
    is_public = BooleanField(_('public'), default=True)
    is_draft = BooleanField(_('draft'), default=False)

    def save(self, obj=None, save=True) -> Brew:
        if obj is None:
            obj = Brew()
        return super(BrewForm, self).save(obj, save)


class ChangeStateForm(BaseForm):
    action = SelectField(
        _('action'), choices=choices.ACTION_CHOICES, default='available'
    )

    buttons = [
        Button(text=_('change'))
    ]
