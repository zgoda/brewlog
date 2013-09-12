from flask import request, flash, url_for, redirect, render_template, abort
from flask_login import current_user, login_required
from flask_babel import gettext as _
from sqlalchemy import desc

from brewlog.models import Brewery, Brew
from brewlog.utils.models import get_or_404, Pagination, paginate
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
    if current_user.is_anonymous():
        query = Brewery.public_query()
    else:
        query = Brewery.public_query(extra_user=current_user)
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'pagination': pagination,
        'breweries': paginate(query.order_by(Brewery.name), page-1, page_size)
    }
    return render_template('brewery/list.html', **ctx)

def brewery(brewery_id, **kwargs):
    brewery = get_or_404(Brewery, brewery_id)
    if not brewery.is_public and (current_user != brewery.brewer):
        abort(404)
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

def brewery_brews(brewery_id):
    page_size = 20
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    brewery = get_or_404(Brewery, brewery_id)
    public_only = False
    if current_user.is_anonymous() or (current_user != brewery.brewer):
        public_only = True
    brews = brewery.all_brews(public_only)
    pagination = Pagination(page, page_size, len(brews))
    ctx = {
        'brewery': brewery,
        'brews': brews,
        'pagination': pagination,
    }
    return render_template('brewery/brews.html', **ctx)

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

def brew(brew_id, **kwargs):
    brew = get_or_404(Brew, brew_id)
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
    if current_user.is_anonymous():
        query = Brew.public_query()
    else:
        query = Brew.public_query(extra_user=current_user)
    pagination = Pagination(page, page_size, query.count())
    context = {
        'pagination': pagination,
        'brews': paginate(query.order_by(desc(Brew.created)), page-1, page_size)
    }
    return render_template('brew/list.html', **context)

def brew_export(brew_id, flavour):
    brew = get_or_404(Brew, brew_id)
    ctx = {
        'brew': brew,
        'flavour': flavour,
        'exported': render_template('brew/export/%s.txt' % flavour, brew=brew)
    }
    return render_template('brew/export.html', **ctx)
