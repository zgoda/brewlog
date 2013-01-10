# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from wtforms import FormField
from wtforms.widgets import TableWidget


class SubformField(FormField):
    widget = TableWidget(class_='subform')
