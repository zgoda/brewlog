#!/usr/bin/env python

import webapp2

import route

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

app = webapp2.WSGIApplication(
        route.routes,
    debug=True)

