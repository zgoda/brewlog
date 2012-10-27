# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import webapp2

from webapp2_extras import jinja2


class BaseRequestHandler(webapp2.RequestHandler):

	@webapp2.cached_property
	def jinja2(self):
		return jinja2.get_jinja2(app=self.app)

	def render_to_response(self, _template, **context):
		rv = self.jinja2.render_template(_template, **context)
		self.response.write(rv)
