from flask import request, flash, url_for, redirect, render_template, abort
from flask_login import current_user
from flaskext.babel import lazy_gettext as _

from brewlog.brewing.models import Brewery
from brewlog.brewing.forms.brewery import BreweryForm
from brewlog.brewing.forms import BrewForm


def brewery_add():
    form = BreweryForm(request.form)
    if request.method == 'POST':
        if form.validate():
            brewery = form.save(user=current_user)
            flash(_('brewery %(name)s created', name=brewery.name))
            next_url = request.args.get('next') or 'brewery-all'
            return redirect(url_for(next_url))
    ctx = {
        'form': form,
    }
    return render_template('brewery/form.html', **ctx)

def brewery_all():
    ctx = {
    }
    return render_template('brewery/list.html', **ctx)

def brewery_details(brewery_id):
    brewery = Brewery.query.get(brewery_id)
    if not brewery:
        abort(404)
    ctx = {
        'brewery': brewery,
        'form': BreweryForm(obj=brewery),
    }
    return render_template('brewery/details.html', **ctx)

def brew_add():
    form = BrewForm(request.form)
    if request.method == 'POST':
        if form.validate():
            brew = form.save(user=current_user)
            flash(_('brew %()s created', name=brew.name))
            next_url = request.args('next')
            if next_url:
                return redirect(url_for(next_url))
            else:
                return redirect(url_for('brewery-details', brewery_id=brew.brewery.id))
    ctx = {
        'form': form,
    }
    return render_template('brew/form.html', **ctx)
