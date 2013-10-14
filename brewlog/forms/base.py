from wtforms import BooleanField
from flask_wtf import Form
from flask_babel import lazy_gettext as _

from brewlog import dbsession as session


class BaseForm(Form):

    def save(self, obj, save=False):
        self.populate_obj(obj)
        if save:
            session.add(obj)
            session.commit()
        return obj


class DeleteForm(BaseForm):
    delete_it = BooleanField(_('delete'), default=False)