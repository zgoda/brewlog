from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField

from ..ext import db
from .utils import Button, Link


class BaseForm(FlaskForm):
    pass


class BaseObjectForm(BaseForm):

    buttons = [
        Button(text=_('save')),
        Link(href='javascript:history.back()', text=_('go back')),
    ]

    def save(self, obj, save=False):
        self.populate_obj(obj)
        if save:
            db.session.add(obj)
            db.session.commit()
        return obj


class DeleteForm(BaseForm):
    delete_it = BooleanField(_('delete'), default=False)

    buttons = [
        Button(text=_('confirm')),
    ]
