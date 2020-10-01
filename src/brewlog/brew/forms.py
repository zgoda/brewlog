from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from wtforms.fields import BooleanField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import InputRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField

from ..models import Brew, Brewery, choices
from ..utils.forms import BaseObjectForm


def user_breweries_query() -> BaseQuery:
    return Brewery.query.filter_by(brewer=current_user).order_by(Brewery.name)


class BaseBrewForm(BaseObjectForm):
    brewery = QuerySelectField(
        'browar', query_factory=user_breweries_query, get_label='name',
        validators=[InputRequired()]
    )
    name = StringField('nazwa', validators=[InputRequired()])
    code = StringField('kod')
    style = StringField('styl', description='opis stylu własnymi słowami')
    bjcp_style_code = StringField('kod stylu BJCP')
    bjcp_style_name = StringField('nazwa stylu BJCP')
    notes = TextAreaField('notatki')
    date_brewed = DateField('data warzenia', validators=[Optional()])
    fermentables = TextAreaField(
        'surowce fermentowalne',
        description='umieść każdą rzecz w oddzielnej linii by uzyskać listę',
    )
    hops = TextAreaField(
        'chmiele',
        description='umieść każdą rzecz w oddzielnej linii by uzyskać listę',
    )
    yeast = TextAreaField(
        'drożdże',
        description='umieść każdą rzecz w oddzielnej linii by uzyskać listę',
    )
    misc = TextAreaField(
        'różne',
        description='umieść każdą rzecz w oddzielnej linii by uzyskać listę',
    )
    mash_steps = TextAreaField(
        'schemat zacierania',
        description='umieść każdą rzecz w oddzielnej linii by uzyskać listę',
    )
    sparging = StringField('wysładzanie')
    hopping_steps = TextAreaField(
        'schemat chmielenia',
        description='umieść każdą rzecz w oddzielnej linii by uzyskać listę',
    )
    boil_time = IntegerField('gotowanie', validators=[Optional()])

    def save(self, obj=None, save=True) -> Brew:
        if obj is None:
            obj = Brew()
        return super(BaseBrewForm, self).save(obj, save)


class CreateBrewForm(BaseBrewForm):
    is_public = BooleanField('publiczna', default=True)
    is_draft = BooleanField('szkic', default=False)


class EditBrewForm(BaseBrewForm):
    final_amount = DecimalField(
        'objętość końcowa', places=1, description='objętość do rozlewu',
        validators=[Optional()]
    )
    bottling_date = DateField('data rozlewu', validators=[Optional()])
    carbonation_type = SelectField(
        'typ nagazowania', choices=choices.CARBONATION_CHOICES,
    )
    carbonation_level = SelectField(
        'poziom nagazowania', choices=choices.CARB_LEVEL_CHOICES,
    )
    carbonation_used = TextAreaField('użyte do nagazowania')
