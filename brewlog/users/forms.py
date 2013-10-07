from flask import current_app
import wtforms as wf
from wtforms.validators import DataRequired, Email, Optional
from flask_babel import lazy_gettext as _

from brewlog.forms.base import BaseForm
from brewlog.models.users import BrewerProfile, IPBoardExportSetup, CustomExportTemplate, CustomLabelTemplate


class ProfileForm(BaseForm):
    first_name = wf.TextField(_('first name'), validators=[Optional()])
    last_name = wf.TextField(_('last name'), validators=[Optional()])
    nick = wf.TextField(_('nick'), validators=[Optional()],
        description=_('one of above fields should be provided or parts of your email address may be seen across the site'))
    email = wf.TextField(_('email'), validators=[DataRequired(), Email()])
    location = wf.TextField(_('location'), validators=[Optional()])
    about_me = wf.TextAreaField(_('about me'), validators=[Optional()])
    is_public = wf.BooleanField(_('profile is public'), validators=[Optional()], default=True,
        description=_('all activity of non-public brewers is hidden on site, they are invisible'))

    def save(self, obj=None):
        if obj is None:
            obj = BrewerProfile()
        return super(ProfileForm, self).save(obj, save=True)


class CustomExportTemplateForm(BaseForm):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    text = wf.TextAreaField(_('text'), validators=[DataRequired()],
        description=_('template text'))
    is_default = wf.BooleanField(_('default'), default=False, validators=[Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = CustomExportTemplate(user=user)
        return super(CustomExportTemplateForm, self).save(obj, save=True)


class CustomLabelTemplateForm(BaseForm):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    cols = wf.IntegerField(_('columns'), validators=[DataRequired()], default=2)
    rows = wf.IntegerField(_('rows'), validators=[DataRequired()], default=5)
    text = wf.TextAreaField(_('text'), validators=[DataRequired()],
        description=_('template text'))
    is_default = wf.BooleanField(_('default'), default=False, validators=[Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = CustomLabelTemplate(user=user)
        return super(CustomLabelTemplateForm, self).save(obj, save=True)


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
