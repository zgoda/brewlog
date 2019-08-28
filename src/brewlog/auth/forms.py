# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_babel import lazy_gettext as _
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired

from ..ext import db
from ..forms.base import BaseForm
from ..models.users import BrewerProfile
from ..security import pwd_context


def _rkw(**extra):
    render_kw = {
        'class_': 'form-control',
    }
    render_kw.update(extra)
    return render_kw


class LoginForm(BaseForm):
    userid = StringField(
        validators=[DataRequired()],
        render_kw=_rkw(placeholder=_('email or login')),
    )
    password = PasswordField(
        validators=[DataRequired()], render_kw=_rkw(placeholder=_('password')),
    )

    def validate(self):
        is_valid = super().validate()
        user_found = password_valid = False
        if is_valid:
            self.user = BrewerProfile.query.filter(
                db.or_(
                    BrewerProfile.email == self.userid.data,
                    BrewerProfile.username == self.userid.data,
                )
            ).first()
            user_found = self.user is not None
            if user_found:
                password_valid = pwd_context.verify(
                    self.password.data, self.user.password
                )
        return is_valid and user_found and password_valid

    def save(self):
        return self.user
