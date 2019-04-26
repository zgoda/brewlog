# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_babel import lazy_gettext as _
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from wtforms_components.validators import Email

from ..forms.base import BaseObjectForm


class ProfileForm(BaseObjectForm):
    first_name = StringField(_('first name'))
    last_name = StringField(_('last name'))
    nick = StringField(_('nick'))
    email = EmailField(_('email'), validators=[DataRequired(), Email()])
    location = StringField(_('location'))
    about_me = TextAreaField(_('about me'))
    is_public = BooleanField(
        _('profile is public'), default=True,
        description=_(
            'all activity of non-public brewers is hidden on site, they are invisible'
        )
    )

    def save(self, obj):
        return super().save(obj, save=True)

    def validate(self):
        result = super().validate()
        has_name = self.first_name.data and self.last_name.data
        has_nick = self.nick.data
        name_valid = True
        if not (has_name or has_nick):
            name_valid = False
            msg = _('please provide full name or nick')
            self.last_name.errors.append(msg)
            self.first_name.errors.append(msg)
            self.nick.errors.append(msg)
        return result and name_valid
