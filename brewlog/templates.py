import math

from flask.ext.babel import format_date

from brewlog.utils import templates
from brewlog.utils.brewing import plato2sg
from brewlog.utils.text import stars2deg


def setup_filters(application):
    pass # no filters yet

def setup_globals(application):
    application.jinja_env.globals.update({
        'format_date': format_date,
        'url_for_other_page': templates.url_for_other_page,
        'pow': math.pow,
        'stars2deg': stars2deg,
        'plato2sg': plato2sg,
    })

def setup_template_extensions(application):
    setup_filters(application)
    setup_globals(application)
