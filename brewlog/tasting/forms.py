import wtforms as wf
from wtforms.fields.html5 import DateField
from flask_babel import lazy_gettext as _
from flask_login import current_user

from ..forms.base import BaseObjectForm
from ..models.tasting import TastingNote


class TastingNoteForm(BaseObjectForm):
    date = DateField(_('date'))
    text = wf.TextAreaField(_('text'))

    def save(self, brew, save=True):
        obj = TastingNote(brew=brew, author=current_user)
        return super(TastingNoteForm, self).save(obj, save)
