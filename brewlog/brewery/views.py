from flask import abort, flash, redirect, render_template, request
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from ..brewery import brewery_bp
from ..brewery.forms import BreweryForm
from ..ext import db
from ..forms.base import DeleteForm
from ..forms.utils import process_success
from ..models import Brewery
from ..utils.pagination import get_page
from ..utils.views import next_redirect
from .utils import BreweryUtils, check_brewery


@brewery_bp.route('/add', methods=['POST', 'GET'], endpoint='add')
@login_required
def brewery_add():
    form = BreweryForm()
    ret = process_success(form, 'brewery.details', 'brewery %(name)s created')
    if ret is not None:
        return ret
    ctx = {
        'form': form,
    }
    return render_template('brewery/form.html', **ctx)


@brewery_bp.route('/<int:brewery_id>/delete', methods=['POST', 'GET'], endpoint='delete')
@login_required
def brewery_delete(brewery_id):
    brewery = Brewery.query.get_or_404(brewery_id)
    if brewery.brewer != current_user:
        abort(403)
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        name = brewery.name
        db.session.delete(brewery)
        db.session.commit()
        flash(_('brewery %(name)s has been deleted', name=name), category='success')
        next_ = next_redirect('profile.breweries', user_id=current_user.id)
        return redirect(next_)
    ctx = {
        'delete_form': form,
        'brewery': brewery,
    }
    return render_template('brewery/delete.html', **ctx)


@brewery_bp.route('/all', endpoint='all')
def brewery_all():
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


@brewery_bp.route('/search', endpoint='search')
def search():
    if current_user.is_anonymous:
        query = BreweryUtils.breweries()
    else:
        query = current_user.breweries
    term = request.args.getlist('q')
    if term:
        query = query.filter(Brewery.name.like(term[0] + '%'))
    query = query.order_by(Brewery.name)
    return BreweryUtils.brewery_search_result(query)


@brewery_bp.route('/<int:brewery_id>', methods=['POST', 'GET'], endpoint='details')
def brewery(brewery_id):
    brewery = check_brewery(brewery_id, current_user)
    form = None
    if request.method == 'POST':
        form = BreweryForm()
        if form.validate_on_submit():
            brewery = form.save(obj=brewery)
            flash(_('brewery %(name)s data updated', name=brewery.name), category='success')
            return redirect(request.path)
    ctx = {
        'brewery': brewery,
        'form': form or BreweryForm(obj=brewery),
    }
    return render_template('brewery/details.html', **ctx)


@brewery_bp.route('/<int:brewery_id>/brews', endpoint='brews')
def brewery_brews(brewery_id):
    page_size = 20
    page = get_page(request)
    brewery = Brewery.query.get_or_404(brewery_id)
    public_only = False
    if current_user.is_anonymous or (current_user != brewery.brewer):
        if not brewery.has_access(current_user):
            abort(404)
        public_only = True
    brewery_brews = brewery.all_brews(public_only=public_only)
    pagination = brewery_brews.paginate(page, page_size)
    ctx = {
        'brewery': brewery,
        'brews': brewery_brews,
        'pagination': pagination,
    }
    return render_template('brewery/brews.html', **ctx)
