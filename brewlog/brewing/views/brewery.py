from flask import url_for, abort, redirect, render_template, request, flash
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from brewlog.db import session as dbsession
from brewlog.models import breweries
from brewlog.models.brewing import Brewery
from brewlog.forms.base import DeleteForm
from brewlog.brewing.forms.brewery import BreweryForm
from brewlog.utils.models import get_or_404, Pagination, paginate, get_page


@login_required
def brewery_add():
    form = BreweryForm(request.form)
    if request.method == 'POST':
        if form.validate():
            brewery = form.save()
            flash(_('brewery %(name)s created', name=brewery.name), category='success')
            return redirect(brewery.absolute_url)
    ctx = {
        'form': form,
    }
    return render_template('brewery/form.html', **ctx)


@login_required
def brewery_delete(brewery_id):
    brewery = get_or_404(Brewery, brewery_id)
    if brewery.brewer != current_user:
        abort(403)
    form = DeleteForm(request.form)
    if request.method == 'POST':
        name = brewery.name
        if form.validate() and form.delete_it.data:
            dbsession.delete(brewery)
            dbsession.commit()
            flash(_('brewery %(name)s has been deleted', name=name), category='success')
            next_ = request.args.get('next') or url_for('profile-breweries', userid=current_user.id)
            return redirect(next_)
    ctx = {
        'delete_form': form,
        'brewery': brewery,
    }
    return render_template('brewery/delete.html', **ctx)


def brewery_all():
    page_size = 20
    page = get_page(request)
    if current_user.is_anonymous():
        query = breweries()
    else:
        query = breweries(extra_user=current_user)
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'pagination': pagination,
        'breweries': paginate(query.order_by(Brewery.name), page-1, page_size)
    }
    return render_template('brewery/list.html', **ctx)


def brewery(brewery_id, **kwargs):
    brewery = get_or_404(Brewery, brewery_id)
    if request.method == 'POST':
        if current_user != brewery.brewer:
            abort(403)
        form = BreweryForm(request.form)
        if form.validate():
            brewery = form.save(obj=brewery)
            flash(_('brewery %(name)s data updated', name=brewery.name), category='success')
            return redirect(brewery.absolute_url)
    if not brewery.has_access(current_user):
        abort(404)
    ctx = {
        'brewery': brewery,
    }
    if current_user == brewery.brewer:
        ctx['form'] = BreweryForm(obj=brewery)
    return render_template('brewery/details.html', **ctx)


def brewery_brews(brewery_id):
    page_size = 20
    page = get_page(request)
    brewery = get_or_404(Brewery, brewery_id)
    public_only = False
    if current_user.is_anonymous() or (current_user != brewery.brewer):
        if not brewery.has_access(current_user):
            abort(404)
        public_only = True
    brewery_brews = brewery.all_brews(public_only)
    pagination = Pagination(page, page_size, len(brewery_brews))
    ctx = {
        'brewery': brewery,
        'brews': brewery_brews,
        'pagination': pagination,
    }
    return render_template('brewery/brews.html', **ctx)
