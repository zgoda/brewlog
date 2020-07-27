from typing import Union

from flask import Response, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..ext import db
from ..models import Brew
from ..utils.forms import DeleteForm
from ..utils.pagination import get_page
from ..utils.views import next_redirect
from . import brew_bp
from .forms import CreateBrewForm, EditBrewForm
from .permissions import AccessManager
from .utils import BrewUtils, list_query_for_user

HINTS = [
    (
        "67-66*C - 90'\n75*C - 15'",
        'jednostopniowe z wygrzewem',
    ),
    (
        "63-61*C - 30'\n73-71*C - 30'\n75*C - 15'",
        'dwustopniowe z wygrzewem',
    ),
    (
        "55-54*C - 10'\n63-61*C - 30'\n73-71*C - 30'\n75*C - 15'",
        'trójstopniowe z wygrzewem',
    ),
]


@brew_bp.route('/add', methods=['POST', 'GET'], endpoint='add')
@login_required
def brew_add() -> Union[str, Response]:
    form = CreateBrewForm()
    if form.validate_on_submit():
        brew = form.save()
        flash(f'warka {brew.name} utworzona', category='success')
        return redirect(url_for('brew.details', brew_id=brew.id))
    ctx = {
        'form': form,
        'mash_hints': HINTS,
    }
    return render_template('brew/form.html', **ctx)


@brew_bp.route('/<int:brew_id>', methods=['POST', 'GET'], endpoint='details')
def brew(brew_id: int) -> Union[str, Response]:
    brew = Brew.query.get_or_404(brew_id)
    is_post = request.method == 'POST'
    AccessManager(brew, is_post).check()
    brew_form = None
    if is_post:
        brew_form = EditBrewForm()
        if brew_form.validate_on_submit():
            brew = brew_form.save(obj=brew)
            flash(
                f'dane warki {brew.full_name} zmienione', category='success',
            )
            return redirect(request.path)
    public_only = brew.brewery.brewer != current_user
    ctx = {
        'brew': brew,
        'utils': BrewUtils,
        'mash_hints': HINTS,
        'notes': brew.notes_to_json(),
        'next': brew.get_next(public_only=public_only),
        'previous': brew.get_previous(public_only=public_only),
        'form': brew_form or EditBrewForm(obj=brew),
    }
    return render_template('brew/details.html', **ctx)


@brew_bp.route('/all', endpoint='all')
def brew_all() -> str:
    page_size = 20
    page = get_page(request)
    if current_user.is_anonymous:
        query = BrewUtils.brew_list_query()
    else:
        query = BrewUtils.brew_list_query(extra_user=current_user)
    query = query.order_by(db.desc(Brew.created))
    pagination = query.paginate(page, page_size)
    context = {
        'pagination': pagination,
        'utils': BrewUtils,
        'user_is_brewer': False,
    }
    return render_template('brew/list.html', **context)


@brew_bp.route('/search', endpoint='search')
def search() -> Response:
    query = list_query_for_user(current_user)
    term = request.args.getlist('q')
    if term:
        query = query.filter(Brew.name.like(term[0] + '%'))
    query = query.order_by(Brew.name)
    return jsonify(BrewUtils.brew_search_result(query))


@brew_bp.route('/<int:brew_id>/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def brew_delete(brew_id: int) -> Union[str, Response]:
    brew = Brew.query.get_or_404(brew_id)
    AccessManager(brew, True).check()
    name = brew.name
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        db.session.delete(brew)
        db.session.commit()
        flash(
            f'warka {name} została usunięta', category='success',
        )
        next_ = next_redirect('profile.brews', user_id=current_user.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'delete_form': form,
    }
    return render_template('brew/delete.html', **ctx)
