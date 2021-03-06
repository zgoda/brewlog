from flask_babel import lazy_gettext as _
from wtforms.fields import StringField, TextAreaField
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import InputRequired, Optional

from ..forms.base import BaseObjectForm
from ..models import FermentationStep


class FermentationStepForm(BaseObjectForm):
    date = DateField(_('date'), validators=[InputRequired()])
    name = StringField(_('name'), validators=[InputRequired()])
    og = DecimalField(_('original gravity'), places=1, validators=[Optional()])
    fg = DecimalField(_('final gravity'), places=1, validators=[Optional()])
    temperature = IntegerField(_('temperature'), validators=[Optional()])
    volume = DecimalField(_('volume collected'), places=1, validators=[Optional()])
    notes = TextAreaField(_('notes'))

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = FermentationStep(brew=brew)
        return super().save(obj, save)
