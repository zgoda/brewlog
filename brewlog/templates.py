import math

from flask_babelex import format_date

from brewlog.utils.brewing import plato2sg
from brewlog.utils.text import stars2deg
from brewlog.utils.pagination import url_for_other_page


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
