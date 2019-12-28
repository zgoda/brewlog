# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_babel import lazy_gettext as _
from flask_login import current_user
from wtforms.fields import TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired

from ..forms.base import BaseObjectForm
from ..models import TastingNote


class TastingNoteForm(BaseObjectForm):
    date = DateField(_('date'), validators=[InputRequired()])
    text = TextAreaField(_('text'), validators=[InputRequired()])

    def save(self, brew, save=True):
        obj = TastingNote(brew=brew, author=current_user)
        return super(TastingNoteForm, self).save(obj, save)
