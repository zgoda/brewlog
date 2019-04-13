import wtforms as wf
from flask_babel import lazy_gettext as _
from flask_login import current_user
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length

from ..forms.base import BaseObjectForm
from ..models import Brewery


class BreweryNameLength(Length):

    def __init__(self):
        super().__init__(
            min=4, max=500,
            message=_('brewery name has to be between 4 and 500 characters long')
        )


class BreweryForm(BaseObjectForm):
    name = wf.StringField(_('name'), validators=[BreweryNameLength(), DataRequired()])
    description = wf.TextAreaField(_('description'))
    established_date = DateField(_('established'))

    def save(self, obj=None):
        if obj is None:
            obj = Brewery(brewer=current_user)
        return super(BreweryForm, self).save(obj, save=True)