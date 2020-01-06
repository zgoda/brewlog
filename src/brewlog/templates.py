import math

from flask_babel import format_date

from ._version import get_version
from .utils.brewing import plato2sg
from .utils.pagination import url_for_other_page
from .utils.text import stars2deg


def setup_globals(application):
    application.jinja_env.globals.update({
        'format_date': format_date,
        'pow': math.pow,
        'stars2deg': stars2deg,
        'plato2sg': plato2sg,
        'url_for_other_page': url_for_other_page,
        'version': get_version(),
    })


def setup_template_extensions(application):
    setup_globals(application)
