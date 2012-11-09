# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf

from forms.base import BaseForm
from models.base import Brewery


class BreweryNameLength(wf.validators.Length):

    def __init__(self):
        return super(BreweryNameLength, self).__init__(min=4, max=500,
            message='brewery name has to be between 4 and 500 characters long')


class BreweryForm(BaseForm):
    name = wf.TextField('name', validators=[BreweryNameLength()])
    description = wf.TextAreaField('description')
    established_date = wf.DateField('established', validators=[wf.validators.Optional()])

    def save(self, user, obj=None):
        if obj is None:
            obj = Brewery(parent=user.key, user=user.key)
        return super(BreweryForm, self).save(user, obj, save=True)
