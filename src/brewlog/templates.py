import math

from flask_babel import format_date, get_locale
from wtforms.fields import HiddenField

from ._version import get_version
from .utils.app import Brewlog
from .utils.brewing import plato2sg
from .utils.pagination import url_for_other_page
from .utils.text import stars2deg


icons = {
    'user': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round" class="feather feather-user">
<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4">
</circle></svg>'''
}


def setup_globals(application: Brewlog):
    application.jinja_env.globals.update({
        'format_date': format_date,
        'get_locale': get_locale,
        'pow': math.pow,
        'stars2deg': stars2deg,
        'plato2sg': plato2sg,
        'url_for_other_page': url_for_other_page,
        'version': get_version(),
        'is_hidden_field': lambda x: isinstance(x, HiddenField),
    })

    @application.context_processor
    def icons():
        return icons


def setup_template_extensions(application: Brewlog):
    setup_globals(application)
