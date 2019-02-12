from datetime import datetime

from flask import (
    abort, flash, jsonify, redirect, render_template,
    render_template_string, request, url_for
)
from flask_babel import gettext as _
from flask_babel import lazy_gettext
from flask_login import current_user, login_required
from markdown import markdown

from . import brew_bp
from ..ext import db
from ..forms.base import DeleteForm
from ..models import brews
from ..models.brewing import Brew, FermentationStep
from ..models.users import CustomLabelTemplate
from ..utils.pagination import get_page
from .forms import BrewForm, ChangeStateForm, FermentationStepForm
from .utils import BrewUtils

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
            flash(_('brew %(name)s data updated', name=brew.name), category='success')
            return redirect(url_for('brew.details', brew_id=brew.id))
    if not brew.has_access(current_user):
        abort(404)
    public_only = current_user not in brew.brewery.brewers
    ctx = {
        'brew': brew,
        'utils': BrewUtils(brew),
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
    if request.accept_mimetypes.best == 'application/json':
        if current_user.is_anonymous:
            query = brews()
        else:
            query = brews(public_only=False, user=current_user)
        query = query.order_by(Brew.name)
        brew_list = []
        for brew_id, name in query.values(Brew.id, Brew.name):
            url = url_for('brew.details', brew_id=brew_id)
            brew_list.append(dict(name=name, url=url))
        return jsonify(brew_list)
    else:
        if current_user.is_anonymous:
            query = brews()
        else:
            query = brews(extra_user=current_user)
        query = query.order_by(db.desc(Brew.created))
        pagination = query.paginate(page, page_size)
        context = {
            'pagination': pagination,
        }
        return render_template('brew/list.html', **context)


@brew_bp.route('/search', endpoint='search')
def search():
    if current_user.is_anonymous:
        query = brews()
    else:
        query = brews(public_only=False, user=current_user)
    term = request.args.getlist('q')
    if term:
        query = query.filter(Brew.name.like(term[0] + '%'))
    query = query.order_by(Brew.name)
    brew_list = []
    for brew_id, name in query.values(Brew.id, Brew.name):
        url = url_for('brew.details', brew_id=brew_id)
        brew_list.append(dict(name=name, url=url))
    return jsonify(brew_list)


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
        next_ = request.args.get('next') or url_for('profile.brews', userid=current_user.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'delete_form': form,
    }
    return render_template('brew/delete.html', **ctx)


@brew_bp.route(
    '/<int:brew_id>/fermentationstep/add',
    methods=['GET', 'POST'], endpoint='fermentationstep_add'
)
@login_required
def fermentation_step_add(brew_id):
    brew = Brew.query.get_or_404(brew_id)
    if brew.brewery.brewer != current_user:
        abort(403)
    form = FermentationStepForm()
    if form.validate_on_submit():
        fstep = form.save(brew=brew, save=False)
        db.session.add(fstep)
        previous_step = fstep.previous()
        if previous_step:
            previous_step.fg = fstep.og
            db.session.add(previous_step)
        if fstep.fg is not None:
            next_step = fstep.next()
            if next_step:
                next_step.og = fstep.fg
                db.session.add(next_step)
        db.session.commit()
        flash(_('fermentation step %(step_name)s for brew %(brew_name)s has been created', step_name=fstep.name,
            brew_name=brew.name), category='success')
        return redirect(url_for('brew.details', brew_id=brew.id))
    ctx = {
        'brew': brew,
        'form': form,
    }
    return render_template('brew/fermentation/form.html', **ctx)


@brew_bp.route('/fermentationstep/<int:fstep_id>', methods=['GET', 'POST'], endpoint='fermentation_step')
@login_required
def fermentation_step(fstep_id):
    fstep = FermentationStep.query.get_or_404(fstep_id)
    if fstep.brew.brewery.brewer != current_user:
        abort(403)
    form = FermentationStepForm()
    if form.validate_on_submit():
        fstep = form.save(fstep.brew, obj=fstep, save=False)
        db.session.add(fstep)
        previous_step = fstep.previous()
        if previous_step:
            previous_step.fg = fstep.og
            db.session.add(previous_step)
        if fstep.fg is not None:
            next_step = fstep.next()
            if next_step:
                next_step.og = fstep.fg
                db.session.add(next_step)
        db.session.commit()
        flash(_('fermentation step %(step_name)s for brew %(brew_name)s has been updated', step_name=fstep.name,
            brew_name=fstep.brew.name), category='success')
        return redirect(url_for('brew.details', brew_id=fstep.brew.id))
    ctx = {
        'form': FermentationStepForm(obj=fstep),
        'fstep': fstep,
    }
    return render_template('brew/fermentation/step.html', **ctx)


@brew_bp.route('/fermentationstep/<int:fstep_id>/delete', methods=['GET', 'POST'], endpoint='fermentationstep_delete')
@login_required
def fermentation_step_delete(fstep_id):
    fstep = FermentationStep.query.get_or_404(fstep_id)
    if fstep.brew.brewery.brewer != current_user:
        abort(403)
    fstep_name = fstep.name
    brew_name = fstep.brew.name
    next_ = url_for('brew.details', brew_id=fstep.brew.id)
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        db.session.delete(fstep)
        db.session.commit()
        flash(_('fermentation step %(fstep_name)s for brew %(brew_name)s has been deleted', fstep_name=fstep_name,
            brew_name=brew_name), category='success')
        return redirect(next_)
    ctx = {
        'fstep': fstep,
        'delete_form': form,
    }
    return render_template('brew/fermentation/step_delete.html', **ctx)


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
