# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from webapp2 import uri_for


def simpleauth_login_required(handler_method):
    def check_login(self, *args, **kwargs):
        if self.request.method != 'GET':
            self.abort(400, detail='The login_required decorator can only be used for GET requests.')

        if self.logged_in:
            handler_method(self, *args, **kwargs)
        else:
            self.session['original_url'] = self.request.url
            self.redirect(uri_for('auth-select-provider'))

    return check_login
