# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import sys
import webapp2

class MainHandler(webapp2.RequestHandler):

    def get(self):
        self.response.write('Hello, world! sys path: %s' % sys.path)
