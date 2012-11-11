# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf
from wtforms.validators import DataRequired, Email, Optional
from webapp2_extras.i18n import lazy_gettext as _

from forms.base import BaseForm
from models.base import BrewerProfile


class ProfileForm(BaseForm):
    first_name = wf.TextField(_('first name'), validators=[Optional()])
    last_name = wf.TextField(_('last name'), validators=[Optional()])
    nick = wf.TextField(_('nick'), validators=[Optional()])
    email = wf.TextField(_('email'), validators=[DataRequired(), Email()])
    location = wf.TextField(_('location'), validators=[Optional()])
    about_me = wf.TextAreaField(_('about me'), validators=[Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = BrewerProfile(parent=user.key)
        return super(ProfileForm, self).save(user, obj, save=True)
