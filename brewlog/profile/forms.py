import wtforms as wf
from flask import flash, redirect
from flask_babel import lazy_gettext as _
from wtforms.validators import DataRequired, Email

from ..forms.base import BaseObjectForm
from ..models import CustomExportTemplate, CustomLabelTemplate


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
        description=_('all activity of non-public brewers is hidden on site, they are invisible')
    )

    def save(self, obj):
        return super(ProfileForm, self).save(obj, save=True)


class CustomTemplateForm(BaseObjectForm):

    def save_and_redirect(self, user, obj=None):
        obj = self.save(user, obj)
        flash(_('your template %(name)s has been saved', name=obj.name), category='success')
        return redirect(obj.absolute_url)


class CustomExportTemplateForm(CustomTemplateForm):
    name = wf.StringField(_('name'), validators=[DataRequired()])
    text = wf.TextAreaField(_('text'), validators=[DataRequired()], description=_('template text'))
    is_default = wf.BooleanField(_('default'), default=False)

    def save(self, user, obj=None):
        if obj is None:
            obj = CustomExportTemplate(user=user)
        return super(CustomExportTemplateForm, self).save(obj, save=True)


class CustomLabelTemplateForm(CustomTemplateForm):
    name = wf.StringField(_('name'), validators=[DataRequired()])
    cols = wf.IntegerField(_('columns'), validators=[DataRequired()], default=2)
    rows = wf.IntegerField(_('rows'), validators=[DataRequired()], default=5)
    width = wf.IntegerField(_('label width'), validators=[DataRequired()], default=90,
        description=_('single label cell width in milimetres'))
    height = wf.IntegerField(_('label height'), validators=[DataRequired()], default=50,
        description=_('single label cell height in milimetres'))
    text = wf.TextAreaField(_('text'), validators=[DataRequired()], description=_('template text'))
    is_default = wf.BooleanField(_('default'), default=False)

    def save(self, user, obj=None):
        if obj is None:
            obj = CustomLabelTemplate(user=user)
        return super(CustomLabelTemplateForm, self).save(obj, save=True)
