import math
from uuid import uuid4

from flask_babel import format_date
from wtforms.fields import HiddenField

from ._version import get_version
from .utils.app import Brewlog
from .utils.brewing import plato2sg
from .utils.pagination import url_for_other_page
from .utils.text import stars2deg


def setup_globals(application: Brewlog):
    application.jinja_env.globals.update({
        'format_date': format_date,
        'pow': math.pow,
        'stars2deg': stars2deg,
        'plato2sg': plato2sg,
        'url_for_other_page': url_for_other_page,
        'version': get_version(),
        'is_hidden_field': lambda x: isinstance(x, HiddenField),
        'cache_buster': uuid4,
    })


def setup_template_extensions(application: Brewlog):
    setup_globals(application)
