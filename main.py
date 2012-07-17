#!/usr/bin/env python

import webapp2

import route

app = webapp2.WSGIApplication(
        route.routes,
    debug=True)

