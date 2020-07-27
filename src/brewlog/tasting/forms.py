from flask_login import current_user
from wtforms.fields import TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired

from ..models import TastingNote
from ..utils.forms import BaseObjectForm


class TastingNoteForm(BaseObjectForm):
    date = DateField('data', validators=[InputRequired()])
    text = TextAreaField('tekst', validators=[InputRequired()])

    def save(self, brew, save=True):
        obj = TastingNote(brew=brew, author=current_user)
        return super(TastingNoteForm, self).save(obj, save)
