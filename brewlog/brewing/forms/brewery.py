import wtforms as wf
from wtforms.fields.html5 import DateField
from wtforms.validators import Length, Optional, DataRequired
from flask.ext.babel import lazy_gettext as _
from flask.ext.login import current_user

from brewlog.forms.base import BaseForm
from brewlog.models.brewing import Brewery


class BreweryNameLength(Length):

    def __init__(self):
        return super(BreweryNameLength, self).__init__(min=4, max=500,
            message=_('brewery name has to be between 4 and 500 characters long'))


class BreweryForm(BaseForm):
    name = wf.TextField(_('name'), validators=[BreweryNameLength(), DataRequired()])
    description = wf.TextAreaField(_('description'), validators=[Optional()])
    established_date = DateField(_('established'), validators=[Optional()])

    def save(self, obj=None):
        if obj is None:
            obj = Brewery(brewer=current_user)
        return super(BreweryForm, self).save(obj, save=True)


class RecipesUploadForm(BaseForm):
    upload_file = wf.FileField(_('recipes file'))
