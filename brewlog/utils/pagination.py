from flask import request, url_for


def url_for_other_page(page):  # pragma: no cover
    args = request.view_args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)
