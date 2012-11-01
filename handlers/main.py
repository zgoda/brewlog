# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from handlers.base import BaseRequestHandler

class MainHandler(BaseRequestHandler):

    def get(self):
        return self.render('base.html')
