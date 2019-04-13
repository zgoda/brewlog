# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import request, url_for


def url_for_other_page(page):
    args = request.view_args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)


def get_page(request, arg_name='p'):
    try:
        return int(request.args.get(arg_name, '1'))
    except ValueError:
        return 1
