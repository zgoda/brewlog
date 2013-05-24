from flask import request, flash, url_for, redirect, render_template, abort
from flask_login import current_user, login_required
from flaskext.babel import lazy_gettext as _

from brewlog.models import Brewery, Brew
from brewlog.brewing.forms.brewery import BreweryForm
from brewlog.brewing.forms.brew import BrewForm


@login_required
def brewery_add():
    form = BreweryForm(request.form)
    if request.method == 'POST':
        if form.validate():
            brewery = form.save()
            flash(_('brewery %(name)s created', name=brewery.name))
            next_url = request.args.get('next')
            if next_url:
                return redirect(url_for(next_url))
            else:
                return redirect(url_for('brewery-details', brewery_id=brewery.id))
    ctx = {
        'form': form,
    }
    return render_template('brewery/form.html', **ctx)

def brewery_all():
    page_size = 20
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    ctx = {
        'breweries': Brewery.select().order_by(Brewery.name).paginate(page, page_size)
    }
    return render_template('brewery/list.html', **ctx)

def brewery(brewery_id):
    brewery = Brewery.get_or_404(brewery_id)
    if request.method == 'POST':
        if current_user.is_anonymous() or (current_user != brewery.brewer):
            abort(403)
        form = BreweryForm(request.form)
        if form.validate():
            brewery = form.save(obj=brewery)
            flash(_('brewery %(name)s data updated', name=brewery.name))
            return redirect(brewery.absolute_url)
    ctx = {
        'brewery': brewery,
    }
    if current_user == brewery.brewer:
        ctx['form'] = BreweryForm(obj=brewery)
    return render_template('brewery/details.html', **ctx)

@login_required
def brew_add():
    form = BrewForm(request.form)
    if request.method == 'POST':
        if form.validate():
            brew = form.save()
            flash(_('brew %(name)s created', name=brew.name))
            return redirect(brew.absolute_url)
    ctx = {
        'form': form,
    }
    return render_template('brew/form.html', **ctx)

def brew(brew_id):
    brew = Brew.get_or_404(brew_id)
    if request.method == 'POST':
        if current_user != brew.brewery.brewer:
            abort(403)
        form = BrewForm(request.form)
        if form.validate():
            brew = form.save(obj=brew)
            flash(_('brew %(name)s data updated', name=brew.name))
            return redirect(brew.absolute_url)
    ctx = {
        'brew': brew,
    }
    if current_user in brew.brewery.brewers:
        ctx['form'] = BrewForm(obj=brew)
    return render_template('brew/details.html', **ctx)

def brew_all():
    page_size = 20
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    context = {
        'brews': Brew.select().where(Brew.is_public == True).order_by(Brew.created.desc()).paginate(page, page_size)
    }
    return render_template('brew/list.html', **context)
