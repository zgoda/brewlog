import validators
from flask_babel import lazy_gettext as _
from wtforms.fields import BooleanField, PasswordField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import EqualTo, InputRequired, ValidationError

from ..ext import db
from ..forms.base import BaseForm, BaseObjectForm
from ..forms.utils import Button, Link


class ProfileForm(BaseObjectForm):
    first_name = StringField(_('first name'))
    last_name = StringField(_('last name'))
    nick = StringField(_('nick'))
    email = EmailField(_('email'), validators=[InputRequired()])
    location = StringField(_('location'))
    about_me = TextAreaField(_('about me'))
    is_public = BooleanField(
        _('profile is public'), default=True,
        description=_(
            'all activity of non-public brewers is hidden on site, they are invisible'
        )
    )

    def validate_email(self, field):
        if not validators.email(field.data):
            raise ValidationError(
                _('value %(value)s is not valid email address', value=field.data)
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


class PasswordChangeForm(BaseForm):
    new_password = PasswordField(_('new password'), validators=[InputRequired()])
    new_password_r = PasswordField(
        _('new password (repeat)'),
        validators=[EqualTo('new_password'), InputRequired()],
    )

    buttons = [
        Button(text=_('save')),
        Link(href='javascript:history.back()', text=_('go back')),
    ]

    def save(self, user):
        user.set_password(self.new_password.data)
        db.session.add(user)
        db.session.commit()
        return user
