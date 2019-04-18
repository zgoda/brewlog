# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_babel import lazy_gettext as _
from wtforms.fields import StringField, TextAreaField
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Optional

from ..forms.base import BaseObjectForm
from ..models import FermentationStep


class FermentationStepForm(BaseObjectForm):
    date = DateField(_('date'), validators=[DataRequired()])
    name = StringField(_('name'), validators=[DataRequired()])
    og = DecimalField(_('original gravity'), places=1, validators=[Optional()])
    fg = DecimalField(_('final gravity'), places=1, validators=[Optional()])
    temperature = IntegerField(_('temperature'), validators=[Optional()])
    volume = DecimalField(_('volume collected'), places=1, validators=[Optional()])
    notes = TextAreaField(_('notes'))

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = FermentationStep(brew=brew)
        return super().save(obj, save)
