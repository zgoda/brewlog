from flask_babel import lazy_gettext as _
from flask_login import current_user
from wtforms.fields import StringField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Optional

from ..forms.base import BaseObjectForm
from ..models import Brewery


class BreweryForm(BaseObjectForm):
    name = StringField(_('name'), validators=[InputRequired()])
    description = TextAreaField(_('description'))
    established_date = DateField(_('established'), validators=[Optional()])

    def save(self, obj=None):
        if obj is None:
            obj = Brewery(brewer=current_user)
        return super(BreweryForm, self).save(obj, save=True)
