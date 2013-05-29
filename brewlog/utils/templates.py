from flask import request, url_for

from brewlog import app

def url_for_other_page(page):
    args = request.view_args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
