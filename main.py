#!/usr/bin/env python

import sys
import os
lib_dir_path = os.path.join(os.path.dirname(__file__), 'lib')
if not lib_dir_path in sys.path:
    sys.path.insert(0, lib_dir_path)


from secrets import SESSION_KEY

app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': 'sess',
        'secret_key': SESSION_KEY,
    },
    'webapp2_extras.auth': {
        'user_attributes': [],
    },
}

import webapp2

import route

app = webapp2.WSGIApplication(route.routes, config=app_config, debug=True)

