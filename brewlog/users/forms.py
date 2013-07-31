from flask import current_app
import wtforms as wf
from wtforms.validators import DataRequired, Email, Optional
from flaskext.babel import lazy_gettext as _

from brewlog.forms.base import BaseForm
from brewlog.models import BrewerProfile, IPBoardExportSetup


class ProfileForm(BaseForm):
    first_name = wf.TextField(_('first name'), validators=[Optional()])
    last_name = wf.TextField(_('last name'), validators=[Optional()])
    nick = wf.TextField(_('nick'), validators=[Optional()],
        description=_('one of above fields should be provided or parts of your email address may be seen across the site'))
    email = wf.TextField(_('email'), validators=[DataRequired(), Email()])
    location = wf.TextField(_('location'), validators=[Optional()])
    about_me = wf.TextAreaField(_('about me'), validators=[Optional()])
    is_public = wf.BooleanField(_('profile is public'), validators=[Optional()], default=True)

    def save(self, obj=None):
        if obj is None:
            obj = BrewerProfile()
        return super(ProfileForm, self).save(obj, save=True)


class IPBoardExportSetupForm(BaseForm):
    service_name = wf.SelectField(_('service name'),
        choices=sorted(current_app.config['IPB_SERVICES'].keys()),
        validators=[DataRequired()])
    topic_id = wf.TextField(_('topic id'), validators=[DataRequired()],
        description=_('enter numeric ID of your topic in an IP.Board based forum to allow posting brew data directly'))

    def save(self, user, obj=None):
        if obj is None:
            obj = IPBoardExportSetup(user=user)
        return super(IPBoardExportSetupForm, self).save(obj, save=True)
