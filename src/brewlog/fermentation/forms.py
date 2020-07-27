from wtforms.fields import StringField, TextAreaField
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import InputRequired, Optional

from ..models import FermentationStep
from ..utils.forms import BaseObjectForm


class FermentationStepForm(BaseObjectForm):
    date = DateField('data', validators=[InputRequired()])
    name = StringField('nazwa', validators=[InputRequired()])
    og = DecimalField('gęstość pocz.', places=1, validators=[Optional()])
    fg = DecimalField('gęstość końc.', places=1, validators=[Optional()])
    temperature = IntegerField('temperatura', validators=[Optional()])
    volume = DecimalField('objętość', places=1, validators=[Optional()])
    notes = TextAreaField('notatki')

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = FermentationStep(brew=brew)
        return super().save(obj, save)
