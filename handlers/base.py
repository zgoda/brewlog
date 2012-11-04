# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import webapp2
from webapp2 import cached_property

from webapp2_extras import jinja2, sessions, auth


class BaseRequestHandler(webapp2.RequestHandler):

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            super(BaseRequestHandler, self).dispatch()
        finally:
            self.session_store.save_sessions(self.response)

    @cached_property
    def session(self):
        return self.session_store.get_session()

    @cached_property
    def auth(self):
        return auth.get_auth()

    @cached_property
    def current_user(self):
        user_dict = self.auth.get_user_by_session()
        if user_dict is None:
            return None
        return self.auth.store.user_model.get_by_id(user_dict['user_id'])

    @cached_property
    def logged_in(self):
        return self.auth.get_user_by_session() is not None

    @cached_property
    def jinja(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, context=None):
        if context is None:
            context = {}
        values = {
            'uri_for': webapp2.uri_for,
            'logged_in': self.logged_in,
            'current_user': self.current_user,
            'flashes': self.session.get_flashes(),
        }
        values.update(context)
        self.response.write(self.jinja.render_template(template_name, **values))

    def head(self, *args):
        """required by Twitter"""
        pass
