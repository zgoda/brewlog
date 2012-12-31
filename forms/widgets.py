# -*- coding: utf-8 -*-

__revision__ = '$Id$'


from wtforms.widgets import ListWidget


class SubformListWidget(ListWidget):

    def __call__(self, field, **kwargs):
        kwargs['class_'] = 'subform'
        return super(SubformListWidget, self).__call__(field, **kwargs)
