import os

from brewlog import make_app

application = make_app(os.environ.get('ENV', None))
