import wtforms as wf
from flask_babel import lazy_gettext as _
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Optional

from ..models import FermentationStep
from ..forms.base import BaseObjectForm


class FermentationStepForm(BaseObjectForm):
    date = DateField(_('date'), validators=[DataRequired()])
    name = wf.StringField(_('name'), validators=[DataRequired()])
    og = DecimalField(_('original gravity'), places=1, validators=[Optional()])
    fg = DecimalField(_('final gravity'), places=1, validators=[Optional()])
    temperature = IntegerField(_('temperature'), validators=[Optional()])
    volume = DecimalField(_('volume collected'), places=1, validators=[Optional()])
    notes = wf.TextAreaField(_('notes'))

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = FermentationStep(brew=brew)
        return super().save(obj, save)
