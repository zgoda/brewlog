from flask_login import current_user
from wtforms.fields import StringField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Optional

from ..models import Brewery
from ..utils.forms import BaseObjectForm


class BreweryForm(BaseObjectForm):
    name = StringField('nazwa', validators=[InputRequired()])
    description = TextAreaField('opis')
    established_date = DateField('data założenia', validators=[Optional()])

    def save(self, obj=None):
        if obj is None:
            obj = Brewery(brewer=current_user)
        return super(BreweryForm, self).save(obj, save=True)
