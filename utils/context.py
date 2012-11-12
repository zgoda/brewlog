# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import os


def get_global_context():
    return {
        'DEV': os.environ['SERVER_SOFTWARE'].startswith('Dev'),
    }
