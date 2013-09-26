from flask import request, flash, url_for, redirect, render_template, abort
from flask_login import current_user, login_required
from flask_babel import gettext as _
from flask_babel import lazy_gettext
from sqlalchemy import desc

from brewlog.db import session as dbsession
from brewlog.models import Brewery, Brew, TastingNote
from brewlog.forms.base import DeleteForm
from brewlog.utils.models import get_or_404, Pagination, paginate
from brewlog.brewing.forms.brewery import BreweryForm
from brewlog.brewing.forms.brew import BrewForm, TastingNoteForm


HINTS = [
    ("67-66*C - 90'\n75*C - 15'", lazy_gettext('single infusion mash w/ mash out')),
    ("63-61*C - 30'\n73-71*C - 30'\n75*C - 15'", lazy_gettext('2-step mash w/ mash out')),
    ("55-54*C - 10'\n63-61*C - 30'\n73-71*C - 30'\n75*C - 15'", lazy_gettext('3-step mash w/ mash out')),
]


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

@login_required
def brewery_delete(brewery_id):
    brewery = get_or_404(Brewery, brewery_id)
    if brewery.brewer != current_user:
        abort(403)
    form = DeleteForm(request.form)
    if request.method == 'POST':
        name = brewery.name
        if form.validate():
            dbsession.delete(brewery)
            dbsession.commit()
            flash(_('brewery %(name)s has been deleted', name=name))
            next_ = request.args.get('next') or url_for('profile-breweries', userid=current_user.id)
            return redirect(next_)
    ctx = {
        'delete_form': form,
        'brewery': brewery,
    }
    return render_template('brewery/delete.html', **ctx)

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
    if request.method == 'POST':
        if current_user != brewery.brewer:
            abort(403)
        form = BreweryForm(request.form)
        if form.validate():
            brewery = form.save(obj=brewery)
            flash(_('brewery %(name)s data updated', name=brewery.name))
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
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    brewery = get_or_404(Brewery, brewery_id)
    public_only = False
    if current_user.is_anonymous() or (current_user != brewery.brewer):
        if not brewery.has_access(current_user):
            abort(404)
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
        'mash_hints': HINTS,
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
    if not brew.has_access(current_user):
        abort(404)
    ctx = {
        'brew': brew,
        'mash_hints': HINTS,
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
    if not brew.has_access(current_user):
        abort(404)
    ctx = {
        'brew': brew,
        'flavour': flavour,
        'exported': render_template('brew/export/%s.txt' % flavour, brew=brew)
    }
    return render_template('brew/export.html', **ctx)

def brew_print(brew_id):
    brew = get_or_404(Brew, brew_id)
    if not brew.has_access(current_user):
        abort(404)
    ctx = {
        'brew': brew,
    }
    return render_template('brew/print.html', **ctx)

def brew_labels(brew_id):
    brew = get_or_404(Brew, brew_id)
    if not brew.has_access(current_user):
        abort(404)
    ctx = {
        'brew': brew,
    }
    return render_template('brew/labels.html', **ctx)

@login_required
def brew_delete(brew_id):
    brew = get_or_404(Brew, brew_id)
    if brew.brewery.brewer != current_user:
        abort(403)
    name = brew.name
    form = DeleteForm(request.form)
    if request.method == 'POST':
        if form.validate():
            dbsession.delete(brew)
            dbsession.commit()
            flash(_('brew %(name)s has been deleted', name=name))
            next_ = request.args.get('next') or url_for('profile-brews', userid=current_user.id)
            return redirect(next_)
    ctx = {
        'brew': brew,
        'delete_form': form,
    }
    return render_template('brew/delete.html', **ctx)

@login_required
def brew_add_tasting_note(brew_id):
    brew = get_or_404(Brew, brew_id)
    if not brew.has_access(current_user):
        abort(403)
    form = TastingNoteForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save(brew)
        flash(_('tasting note for %(brew)s saved', brew=brew.name))
        next_ = request.args.get('next') or url_for('brew-details', brew_id=brew.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'form': form,
    }
    return render_template('brew/tasting_note.html', **ctx)

@login_required
def brew_delete_tasting_note(note_id):
    note = get_or_404(TastingNote, note_id)
    if current_user not in (note.author, note.brew.brewery.brewer):
        abort(403)
    brew = note.brew
    form = DeleteForm(request.form)
    if request.method == 'POST':
        if form.validate():
            dbsession.delete(note)
            dbsession.commit()
            flash(_('tasting note for brew %(brew)s has been deleted', brew=brew.name))
            next_ = request.args.get('next') or url_for('brew-details', brew_id=brew.id)
            return redirect(next_)
    ctx = {
        'brew': brew,
        'note': note,
        'delete_form': form,
    }
    return render_template('brew/tasting_note_delete.html', **ctx)
