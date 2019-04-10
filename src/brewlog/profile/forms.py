import wtforms as wf
from flask_babel import lazy_gettext as _
from wtforms.validators import DataRequired, Email

from ..forms.base import BaseObjectForm


class ProfileForm(BaseObjectForm):
    first_name = wf.StringField(_('first name'))
    last_name = wf.StringField(_('last name'))
    nick = wf.StringField(
        _('nick'), description=_('one of above fields should be provided')
    )
    email = wf.StringField(_('email'), validators=[DataRequired(), Email()])
    location = wf.StringField(_('location'))
    about_me = wf.TextAreaField(_('about me'))
    is_public = wf.BooleanField(
        _('profile is public'), default=True,
        description=_(
            'all activity of non-public brewers is hidden on site, they are invisible'
        )
    )

    def save(self, obj):
        return super().save(obj, save=True)
