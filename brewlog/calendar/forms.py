import wtforms as wf
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateField
from flask_babelex import lazy_gettext as _

from brewlog.forms.base import BaseForm
from brewlog.calendar import choices
from brewlog.models.calendar import Event


class EventForm(BaseForm):
    date = DateField(_('date'), validators=[DataRequired()])
    title = wf.TextField(_('title'), validators=[DataRequired()])
    description = wf.TextAreaField(_('description'), validators=[Optional()])
    event_type = wf.SelectField(_('event type'), choices=choices.EVENT_TYPE_CHOICES, validators=[Optional()])
    is_public = wf.BooleanField(_('public'), default=True)

    def save(self, brew, obj=None, save=True):
        if obj is None:
            obj = Event(brew=brew)
        return super(EventForm, self).save(obj, save)
