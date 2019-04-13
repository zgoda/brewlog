# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import math

from flask_babel import format_date

from .utils.brewing import plato2sg
from .utils.text import stars2deg
from .utils.pagination import url_for_other_page


def setup_filters(application):
    pass  # no filters yet


def setup_globals(application):
    application.jinja_env.globals.update({
        'format_date': format_date,
        'pow': math.pow,
        'stars2deg': stars2deg,
        'plato2sg': plato2sg,
        'url_for_other_page': url_for_other_page,
    })


def setup_template_extensions(application):
    setup_filters(application)
    setup_globals(application)
