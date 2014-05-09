from flask import request, abort, render_template, redirect, url_for, flash
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _
from sqlalchemy import desc
import markdown

from brewlog.db import session as dbsession
from brewlog.utils.models import get_or_404, Pagination, paginate, get_page
from brewlog.forms.base import DeleteForm
from brewlog.models import tasting_notes
from brewlog.models.brewing import Brew
from brewlog.models.tasting import TastingNote
from brewlog.tasting.forms import TastingNoteForm


def all():
    page_size = 20
    page = get_page(request)
    if current_user.is_anonymous():
        query = tasting_notes()
    else:
        query = tasting_notes(extra_user=current_user)
    pagination = Pagination(page, page_size, query.count())
    context = {
        'public_only': True,
        'pagination': pagination,
        'notes': paginate(query.order_by(desc(TastingNote.date)), page-1, page_size)
    }
    return render_template('tasting/list.html', **context)


@login_required
def brew_add_tasting_note(brew_id):
    brew = get_or_404(Brew, brew_id)
    if not brew.has_access(current_user):
        abort(403)
    form = TastingNoteForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save(brew)
        flash(_('tasting note for %(brew)s saved', brew=brew.name), category='success')
        next_ = request.args.get('next') or url_for('brew-details', brew_id=brew.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'form': form,
    }
    return render_template('tasting/tasting_note.html', **ctx)


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
            flash(_('tasting note for brew %(brew)s has been deleted', brew=brew.name), category='success')
            next_ = request.args.get('next') or url_for('brew-details', brew_id=brew.id)
            return redirect(next_)
    ctx = {
        'brew': brew,
        'note': note,
        'delete_form': form,
    }
    return render_template('tasting/tasting_note_delete.html', **ctx)


def brew_load_tasting_note_text():
    provided_id = request.args.get('id')
    if not provided_id:
        abort(400)
    note_id = provided_id.rsplit('_', 1)[-1]
    note = TastingNote.query.get(note_id)
    if note is None:
        abort(404)
    return note.text


@login_required
def brew_update_tasting_note():
    provided_id = request.form.get('id')
    if not provided_id:
        abort(400)
    note_id = provided_id.rsplit('_', 1)[-1]
    note = TastingNote.query.get(note_id)
    if note is None:
        abort(404)
    if not note.brew.has_access(current_user) or not (current_user in (note.author, note.brew.brewery.brewer)):
        abort(403)
    value = request.form.get('value', '').strip()
    if value:
        note.text = value
        dbsession.add(note)
        dbsession.commit()
        return markdown.markdown(value, safe_mode='remove')
    return note.text_html
