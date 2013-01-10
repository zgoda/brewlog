# -*- coding: utf-8 -*-

__revision__ = '$Id$'


from wtforms.widgets import TableWidget


class SubformTableWidget(TableWidget):

    def __call__(self, field, **kwargs):
        kwargs['class_'] = 'subform'
        return super(SubformTableWidget, self).__call__(field, **kwargs)
