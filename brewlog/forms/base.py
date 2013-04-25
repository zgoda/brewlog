# -*- coding: utf-8 -*-

from wtforms import Form

from brewlog import session


class BaseSubform(Form):

    def item_from_data(self):
        obj = self._model_class()
        non_empty_fields = []
        for field_name, field in self._fields.items():
            setattr(obj, field_name, field.data)
            if field.data:
                non_empty_fields.append(field_name)
        if set(non_empty_fields) >= set(self._required):
            return obj
        return None


class BaseForm(Form):

    def save(self, obj, save=False):
        kw = {}
        for field_name, field in self._fields.items():
            kw[field_name] = field.data
        obj.populate(**kw)
        if save:
            session.add(obj)
            session.commit()
        return obj
