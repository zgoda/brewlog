import datetime

from flask import current_app, session
from wtforms import BooleanField, Form
from wtforms.csrf.session import SessionCSRF
from flask.ext.babel import lazy_gettext as _

from brewlog import db


class BaseForm(Form):

    def __init__(self, *args, **kwargs):
        if not 'meta' in kwargs:
            kwargs['meta'] = dict(
                csrf=current_app.config['CSRF_ENABLED'],
                csrf_class=SessionCSRF,
                csrf_secret=current_app.config['CSRF_SESSION_KEY'],
                csrf_time_limit=datetime.timedelta(minutes=20),
                csrf_context=session,
            )
        return super(BaseForm, self).__init__(*args, **kwargs)

    def save(self, obj, save=False):
        self.populate_obj(obj)
        if save:
            db.session.add(obj)
            db.session.commit()
        return obj


class DeleteForm(BaseForm):
    delete_it = BooleanField(_('delete'), default=False)
