from flask import abort, flash, redirect, render_template, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from . import ferm_bp
from ..ext import db
from ..forms.base import DeleteForm
from ..models import Brew, FermentationStep
from .forms import FermentationStepForm
from .utils import update_steps_gravity


@ferm_bp.route(
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
        previous_step = fstep.previous_step()
        if previous_step:
            previous_step.fg = fstep.og
            db.session.add(previous_step)
        update_steps_gravity(fstep)
        db.session.commit()
        flash(_(
            'fermentation step %(step_name)s for brew %(brew_name)s has been created',
            step_name=fstep.name,
            brew_name=brew.name
        ), category='success')
        return redirect(url_for('brew.details', brew_id=brew.id))
    ctx = {
        'brew': brew,
        'form': form,
    }
    return render_template('fermentation/form.html', **ctx)


@ferm_bp.route(
    '/fermentationstep/<int:fstep_id>', methods=['GET', 'POST'],
    endpoint='fermentation_step'
)
@login_required
def fermentation_step(fstep_id):
    fstep = FermentationStep.query.get_or_404(fstep_id)
    if fstep.brew.brewery.brewer != current_user:
        abort(403)
    form = FermentationStepForm()
    if form.validate_on_submit():
        fstep = form.save(fstep.brew, obj=fstep, save=False)
        db.session.add(fstep)
        previous_step = fstep.previous_step()
        if previous_step:
            previous_step.fg = fstep.og
            db.session.add(previous_step)
        update_steps_gravity(fstep)
        db.session.commit()
        flash(
            _(
                'fermentation step %(step_name)s for brew %(brew_name)s '
                'has been updated',
                step_name=fstep.name, brew_name=fstep.brew.name
            ),
            category='success'
        )
        return redirect(url_for('brew.details', brew_id=fstep.brew.id))
    ctx = {
        'form': FermentationStepForm(obj=fstep),
        'fstep': fstep,
    }
    return render_template('fermentation/step.html', **ctx)


@ferm_bp.route(
    '/fermentationstep/<int:fstep_id>/delete', methods=['GET', 'POST'],
    endpoint='fermentationstep_delete'
)
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
        flash(
            _(
                'fermentation step %(fstep_name)s for brew %(brew_name)s '
                'has been deleted',
                fstep_name=fstep_name, brew_name=brew_name
            ),
            category='success'
        )
        return redirect(next_)
    ctx = {
        'fstep': fstep,
        'delete_form': form,
    }
    return render_template('fermentation/step_delete.html', **ctx)
