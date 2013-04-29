# -*- coding: utf-8 -*-

import wtforms as wf
from wtforms.validators import DataRequired, Email, Optional
from flaskext.babel import lazy_gettext as _

from brewlog.forms.base import BaseForm
from brewlog.users.models import BrewerProfile


class ProfileForm(BaseForm):
    first_name = wf.TextField(_('first name'), validators=[Optional()])
    last_name = wf.TextField(_('last name'), validators=[Optional()])
    nick = wf.TextField(_('nick'), validators=[Optional()])
    email = wf.TextField(_('email'), validators=[DataRequired(), Email()])
    location = wf.TextField(_('location'), validators=[Optional()])
    about_me = wf.TextAreaField(_('about me'), validators=[Optional()])

    def save(self, obj=None):
        if obj is None:
            obj = BrewerProfile()
        return super(ProfileForm, self).save(obj, save=True)
