from flask import request, flash, url_for, redirect, render_template
from flask_login import current_user
from flaskext.babel import lazy_gettext as _

from brewlog.brewing.forms.brewery import BreweryForm


def brewery_add():
    form = BreweryForm(request.form)
    if request.method == 'POST':
        if form.validate():
            brewery = form.save(user=current_user)
            flash(_('brewery %s created') % brewery.name)
            next_url = request.args.get('next') or 'brewery-all'
            return redirect(url_for(next_url))
    ctx = {
        'form': form,
    }
    return render_template('brewery/form.html', **ctx)
