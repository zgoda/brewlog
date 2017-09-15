from flask_wtf import FlaskForm as Form
from wtforms import BooleanField
from flask_babel import lazy_gettext as _

from brewlog.ext import db


class BaseForm(Form):
    pass


class BaseObjectForm(BaseForm):

    def save(self, obj, save=False):
        self.populate_obj(obj)
        if save:
            db.session.add(obj)
            db.session.commit()
        return obj


class DeleteForm(BaseForm):
    delete_it = BooleanField(_('delete'), default=False)
