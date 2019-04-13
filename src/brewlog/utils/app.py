# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import Flask


class Brewlog(Flask):

    @property
    def jinja_options(self):
        options = dict(super().jinja_options)
        options.update({
            'trim_blocks': True,
            'lstrip_blocks': True,
        })
        return options

    def select_jinja_autoescape(self, filename):
        orig_select = super().select_jinja_autoescape(filename)
        return orig_select or filename.endswith(('.jinja', '.jinja2', '.j2'))
