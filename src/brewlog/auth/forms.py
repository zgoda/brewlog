from flask import session
from flask_babel import lazy_gettext as _
from flask_login import login_user
from wtforms.fields import Field, PasswordField, StringField
from wtforms.validators import EqualTo, InputRequired, ValidationError

from ..ext import db
from ..forms.base import BaseForm
from ..forms.utils import Button
from ..models.users import BrewerProfile
from .utils import send_password_reset_email


def _rkw(**extra: str) -> dict:
    render_kw = {
        'class_': 'form-control',
    }
    render_kw.update(extra)
    return render_kw


class RegistrationForm(BaseForm):
    username = StringField(_('user name'), validators=[InputRequired()])
    password1 = PasswordField(_('password'), validators=[InputRequired()])
    password2 = PasswordField(
        _('password (repeat)'), validators=[InputRequired(), EqualTo('password1')]
    )

    buttons = [
        Button(icon='user-alt', text=_('register'))
    ]

    def validate_username(self, field: Field):
        if BrewerProfile.query.filter_by(username=field.data).count() > 0:
            raise ValidationError(_('name is already taken'))

    def save(self) -> BrewerProfile:
        user = BrewerProfile(username=self.username.data)
        user.set_password(self.password1.data)
        db.session.add(user)
        db.session.commit()
        return user


class LoginForm(BaseForm):
    userid = StringField(
        validators=[InputRequired()],
        render_kw=_rkw(placeholder=_('email or login')),
    )
    password = PasswordField(
        validators=[InputRequired()], render_kw=_rkw(placeholder=_('password')),
    )

    def validate(self) -> bool:
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
                password_valid = self.user.check_password(self.password.data)
        return is_valid and user_found and password_valid

    def save(self) -> BrewerProfile:
        login_user(self.user)
        session.permanent = True
        return self.user


class ForgotPassword(BaseForm):
    email1 = StringField(_('email'), validators=[InputRequired()])
    email2 = StringField(
        _('email (repeat)'), validators=[InputRequired(), EqualTo('email1')]
    )

    buttons = [
        Button(icon='at', text=_('send'))
    ]

    def save(self):
        return send_password_reset_email(self.email1.data)
