# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import webapp2

class MainHandler(webapp2.RequestHandler):

    def get(self):
        self.response.write('Hello, world!')