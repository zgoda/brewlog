#!/usr/bin/env python

import sys
import os
lib_dir_path = os.path.join(os.path.dirname(__file__), 'lib')
if not lib_dir_path in sys.path:
    sys.path.insert(0, lib_dir_path)

import webapp2

import route

app = webapp2.WSGIApplication(route.routes, debug=True)

