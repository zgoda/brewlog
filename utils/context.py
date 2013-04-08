# -*- coding: utf-8 -*-

import os


def get_global_context():
    return {
        'DEV': os.environ['SERVER_SOFTWARE'].startswith('Dev'),
    }
