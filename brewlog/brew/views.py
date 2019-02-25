from datetime import datetime

from flask import (
    abort, flash, redirect, render_template, render_template_string, request,
    url_for,
)
from flask_babel import gettext as _
from flask_babel import lazy_gettext
from flask_login import current_user, login_required
from markdown import markdown

from . import brew_bp
from ..ext import db
from ..forms.base import DeleteForm
from ..models import Brew, CustomLabelTemplate
from ..utils.pagination import get_page
from ..utils.views import next_redirect
from .forms import BrewForm, ChangeStateForm
from .utils import BrewUtils, list_query_for_user

HINTS = [
    ("67-66*C - 90'\n75*C - 15'", lazy_gettext('single infusion mash w/ mash out')),
    ("63-61*C - 30'\n73-71*C - 30'\n75*C - 15'", lazy_gettext('2-step mash w/ mash out')),
    ("55-54*C - 10'\n63-61*C - 30'\n73-71*C - 30'\n75*C - 15'", lazy_gettext('3-step mash w/ mash out')),
]


@brew_bp.route('/add', methods=['POST', 'GET'], endpoint='add')
@login_required
def brew_add():
    form = BrewForm()
    if form.validate_on_submit():
        brew = form.save()
        flash(_('brew %(name)s created', name=brew.name), category='success')
        return redirect(url_for('brew.details', brew_id=brew.id))
    ctx = {
        'form': form,
        'mash_hints': HINTS,
    }
    return render_template('brew/form.html', **ctx)


@brew_bp.route('/<int:brew_id>', methods=['POST', 'GET'], endpoint='details')
def brew(brew_id, **kwargs):
    brew = Brew.query.get_or_404(brew_id)
    if request.method == 'POST':
        if current_user not in brew.brewery.brewers:
            abort(403)
        form = BrewForm()
        if form.validate_on_submit():
            brew = form.save(obj=brew)
            flash(_('brew %(name)s data updated', name=brew.full_name), category='success')
            return redirect(request.path)
    if not brew.has_access(current_user):
        abort(404)
    public_only = current_user not in brew.brewery.brewers
    ctx = {
        'brew': brew,
        'utils': BrewUtils,
        'mash_hints': HINTS,
        'notes': brew.notes_to_json(),
        'next': brew.get_next(public_only=public_only),
        'previous': brew.get_previous(public_only=public_only),
    }
    if current_user in brew.brewery.brewers:
        ctx['form'] = BrewForm(obj=brew)
        if brew.current_state[0] in (brew.STATE_FINISHED, brew.STATE_TAPPED, brew.STATE_MATURING):
            ctx['action_form'] = ChangeStateForm()
    return render_template('brew/details.html', **ctx)


@brew_bp.route('/all', endpoint='all')
def brew_all():
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
    }
    return render_template('brew/list.html', **context)


@brew_bp.route('/prefetch', endpoint='prefetch')
def bloodhound_prefetch():
    query = list_query_for_user(current_user)
    query = query.order_by(Brew.name)
    return BrewUtils.brew_search_result(query)


@brew_bp.route('/search', endpoint='search')
def search():
    query = list_query_for_user(current_user)
    term = request.args.getlist('q')
    if term:
        query = query.filter(Brew.name.like(term[0] + '%'))
    query = query.order_by(Brew.name)
    return BrewUtils.brew_search_result(query)


@brew_bp.route('/<int:brew_id>/export/<flavour>', endpoint='export')
def brew_export(brew_id, flavour):
    brew = Brew.query.get_or_404(brew_id)
    if not brew.has_access(current_user):
        abort(403)
    ctx = {
        'brew': brew,
        'flavour': flavour,
        'exported': render_template('brew/export/%s.txt' % flavour, brew=brew)
    }
    return render_template('brew/export.html', **ctx)


@brew_bp.route('/<int:brew_id>/print', endpoint='print')
def brew_print(brew_id):
    brew = Brew.query.get_or_404(brew_id)
    if not brew.has_access(current_user):
        abort(403)
    ctx = {
        'brew': brew,
    }
    return render_template('brew/print.html', **ctx)


@brew_bp.route('/<int:brew_id>/labels', endpoint='labels')
def brew_labels(brew_id):
    brew = Brew.query.get_or_404(brew_id)
    if not brew.has_access(current_user):
        abort(403)
    ctx = {
        'brew': brew,
        'custom_templates': [],
        'rendered_cell': None,
        'rows': 5,
        'cols': 2,
        'cell_style': 'width:90mm;height:50mm',
        'current_template': 0,
    }
    if current_user.is_authenticated:
        ctx['custom_templates'] = current_user.custom_label_templates.order_by(CustomLabelTemplate.name).all()
        use_template = request.args.get('template')
        if use_template is not None:
            template_obj = current_user.custom_label_templates.filter_by(id=use_template).one()
            if template_obj is not None:
                cs = 'width:%(width)smm;min-width:%(width)smm;height:%(height)smm;min-height:%(height)s' % \
                    {'width': template_obj.width, 'height': template_obj.height}
                custom_data = dict(
                    rendered_cell=render_template_string(markdown(template_obj.text, safe_mode='remove'), brew=brew),
                    rows=template_obj.rows,
                    cols=template_obj.cols,
                    cell_style=cs,
                    current_template=template_obj.id,
                )
                ctx.update(custom_data)
    return render_template('brew/labels.html', **ctx)


@brew_bp.route('/<int:brew_id>/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def brew_delete(brew_id):
    brew = Brew.query.get_or_404(brew_id)
    if brew.brewery.brewer != current_user:
        abort(403)
    name = brew.name
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        db.session.delete(brew)
        db.session.commit()
        flash(_('brew %(name)s has been deleted', name=name), category='success')
        next_ = next_redirect('profile.brews', userid=current_user.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'delete_form': form,
    }
    return render_template('brew/delete.html', **ctx)


@brew_bp.route('/<int:brew_id>/chgstate', methods=['POST'], endpoint='chgstate')
@login_required
def change_state(brew_id):
    brew = Brew.query.get_or_404(brew_id)
    if brew.brewery.brewer != current_user:
        abort(403)
    form = ChangeStateForm()
    now = datetime.utcnow()
    action = form.data['action']
    if action == 'tap':
        brew.tapped = now
        brew.finished = None
    elif action in ('untap', 'available'):
        brew.finished = None
        brew.tapped = None
    elif action == 'finish':
        brew.finished = now
    db.session.add(brew)
    db.session.commit()
    return redirect(url_for('brew.details', brew_id=brew.id))
