import wtforms as wf
from wtforms.fields.html5 import DateField
from flask_babelex import lazy_gettext as _
from flask_login import current_user

from brewlog.forms.base import BaseForm
from brewlog.models.tasting import TastingNote


class TastingNoteForm(BaseForm):
    date = DateField(_('date'))
    text = wf.TextAreaField(_('text'))

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = TastingNote(brew=brew, author=current_user)
        return super(TastingNoteForm, self).save(obj, save)
