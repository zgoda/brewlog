# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf


class BreweryForm(wf.Form):
    name = wf.TextField('name', [wf.validators.Length(min=4, max=500, message='brewery name has to be between 4 and 500 characters long')])
    description = wf.TextAreaField('description')