# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from wtforms import Form


class BaseForm(Form):

    def save(self, user, obj, save=False):
        kw = {}
        for field_name, field in self._fields.items():
            kw[field_name] = field.data
        obj.populate(**kw)
        if save:
            obj.put()
        return obj
