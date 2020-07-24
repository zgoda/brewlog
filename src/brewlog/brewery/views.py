from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from ..ext import db
from ..models import Brewery
from ..utils.forms import DeleteForm
from ..utils.pagination import get_page
from ..utils.views import next_redirect
from . import brewery_bp
from .forms import BreweryForm
from .permissions import AccessManager
from .utils import BreweryUtils


@brewery_bp.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    form = BreweryForm()
    if form.validate_on_submit():
        brewery = form.save()
        flash(_('brewery %(name)s created', name=brewery.name), category='success')
        return redirect(url_for('brewery.details', brewery_id=brewery.id))
    ctx = {
        'form': form,
    }
    return render_template('brewery/form.html', **ctx)


@brewery_bp.route('/<int:brewery_id>/delete', methods=['POST', 'GET'])
def delete(brewery_id):
    brewery = Brewery.query.get_or_404(brewery_id)
    AccessManager(brewery, True).check()
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        name = brewery.name
        db.session.delete(brewery)
        db.session.commit()
        flash(
            _('brewery %(name)s has been deleted', name=name), category='success',
        )
        next_ = next_redirect('profile.breweries', user_id=current_user.id)
        return redirect(next_)
    ctx = {
        'delete_form': form,
        'brewery': brewery,
    }
    return render_template('brewery/delete.html', **ctx)


@brewery_bp.route('/all', endpoint='all')
def all_breweries():
    page_size = 20
    page = get_page(request)
    if current_user.is_anonymous:
        query = BreweryUtils.breweries()
    else:
        query = BreweryUtils.breweries(extra_user=current_user)
    query = query.order_by(Brewery.name)
    pagination = query.paginate(page, page_size)
    ctx = {
        'pagination': pagination,
    }
    return render_template('brewery/list.html', **ctx)


@brewery_bp.route('/search')
def search():
    if current_user.is_anonymous:
        query = BreweryUtils.breweries()
    else:
        query = current_user.breweries
    term = request.args.getlist('q')
    if term:
        query = query.filter(Brewery.name.like(term[0] + '%'))
    query = query.order_by(Brewery.name)
    return jsonify(BreweryUtils.brewery_search_result(query))


@brewery_bp.route('/<int:brewery_id>', methods=['POST', 'GET'])
def details(brewery_id):
    brewery = Brewery.query.get_or_404(brewery_id)
    is_post = request.method == 'POST'
    AccessManager(brewery, is_post).check()
    form = None
    if is_post:
        form = BreweryForm()
        if form.validate_on_submit():
            brewery = form.save(obj=brewery)
            flash(
                _('brewery %(name)s data updated', name=brewery.name),
                category='success',
            )
            return redirect(request.path)
    ctx = {
        'brewery': brewery,
        'utils': BreweryUtils(brewery),
        'form': form or BreweryForm(obj=brewery),
    }
    return render_template('brewery/details.html', **ctx)


@brewery_bp.route('/<int:brewery_id>/brews')
def brews(brewery_id):
    brewery = Brewery.query.get_or_404(brewery_id)
    AccessManager(brewery, False).check()
    page_size = 20
    page = get_page(request)
    utils = BreweryUtils(brewery)
    public_only = False
    if current_user.is_anonymous or (current_user != brewery.brewer):
        public_only = True
    brewery_brews = utils.recent_brews(public_only=public_only, limit=None)
    pagination = brewery_brews.paginate(page, page_size)
    ctx = {
        'brewery': brewery,
        'brews': brewery_brews,
        'pagination': pagination,
    }
    return render_template('brewery/brews.html', **ctx)
