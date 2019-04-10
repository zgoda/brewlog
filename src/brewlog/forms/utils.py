import inspect

from flask import current_app, flash, redirect, url_for
from flask_babel import lazy_gettext


def process_success(form, endpoint, flash_message):
    if form.validate_on_submit():
        obj = form.save()
        flash(lazy_gettext(flash_message, name=obj.name), category='success')
        view_func = current_app.view_functions[endpoint]
        arg_name = inspect.getfullargspec(view_func).args[0]
        kw = {
            arg_name: obj.id,
        }
        return redirect(url_for(endpoint, **kw))
