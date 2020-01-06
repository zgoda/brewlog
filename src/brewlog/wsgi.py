import os

from .app import make_app

application = make_app(os.environ.get('ENV'))
