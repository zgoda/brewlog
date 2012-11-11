# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf
from wtforms.validators import Length, Optional, DataRequired
from webapp2_extras.i18n import lazy_gettext as _

from forms.base import BaseForm
from models.base import Brewery


class BreweryNameLength(Length):

    def __init__(self):
        return super(BreweryNameLength, self).__init__(min=4, max=500,
            message=_('brewery name has to be between 4 and 500 characters long'))


class BreweryForm(BaseForm):
    name = wf.TextField(_('name'), validators=[BreweryNameLength(), DataRequired()])
    description = wf.TextAreaField(_('description'), validators=[Optional()])
    established_date = wf.DateField(_('established'), validators=[Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = Brewery(parent=user.key)
        return super(BreweryForm, self).save(user, obj, save=True)
