import wtforms as wf
from wtforms.validators import DataRequired, Email, Optional
from flask_babelex import lazy_gettext as _

from brewlog.forms.base import BaseObjectForm
from brewlog.models.users import CustomExportTemplate, CustomLabelTemplate


class ProfileForm(BaseObjectForm):
    first_name = wf.TextField(_('first name'), validators=[Optional()])
    last_name = wf.TextField(_('last name'), validators=[Optional()])
    nick = wf.TextField(_('nick'), validators=[Optional()],
        description=_('one of above fields should be provided'))
    email = wf.TextField(_('email'), validators=[DataRequired(), Email()])
    location = wf.TextField(_('location'), validators=[Optional()])
    about_me = wf.TextAreaField(_('about me'), validators=[Optional()])
    is_public = wf.BooleanField(_('profile is public'), validators=[Optional()], default=True,
        description=_('all activity of non-public brewers is hidden on site, they are invisible'))

    def save(self, obj):
        return super(ProfileForm, self).save(obj, save=True)


class CustomExportTemplateForm(BaseObjectForm):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    text = wf.TextAreaField(_('text'), validators=[DataRequired()], description=_('template text'))
    is_default = wf.BooleanField(_('default'), default=False, validators=[Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = CustomExportTemplate(user=user)
        return super(CustomExportTemplateForm, self).save(obj, save=True)


class CustomLabelTemplateForm(BaseObjectForm):
    name = wf.TextField(_('name'), validators=[DataRequired()])
    cols = wf.IntegerField(_('columns'), validators=[DataRequired()], default=2)
    rows = wf.IntegerField(_('rows'), validators=[DataRequired()], default=5)
    width = wf.IntegerField(_('label width'), validators=[DataRequired()], default=90,
        description=_('single label cell width in milimetres'))
    height = wf.IntegerField(_('label height'), validators=[DataRequired()], default=50,
        description=_('single label cell height in milimetres'))
    text = wf.TextAreaField(_('text'), validators=[DataRequired()], description=_('template text'))
    is_default = wf.BooleanField(_('default'), default=False, validators=[Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = CustomLabelTemplate(user=user)
        return super(CustomLabelTemplateForm, self).save(obj, save=True)
