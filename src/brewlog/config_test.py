# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

TESTING = True
BABEL_DEFAULT_LOCALE = 'en_US'
CSRF_ENABLED = False
WTF_CSRF_ENABLED = CSRF_ENABLED
LOGIN_DISABLED = False
SQLALCHEMY_DATABASE_URI = 'sqlite://'

AUTH_CONFIG = {
    'google': ('app_id', 'app_secret'),
    'facebook': ('app_id', 'app_secret'),
    'github': ('app_id', 'app_secret'),
}
