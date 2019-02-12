import markdown
from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from . import tasting_bp
from ..ext import db
from ..forms.base import DeleteForm
from ..models import tasting_notes
from ..models.brewing import Brew
from ..models.tasting import TastingNote
from ..utils.pagination import get_page
from .forms import TastingNoteForm


@tasting_bp.route('/all', endpoint='all')
def all():
    page_size = 20
    page = get_page(request)
    if current_user.is_anonymous:
        query = tasting_notes()
    else:
        query = tasting_notes(extra_user=current_user)
    query = query.order_by(db.desc(TastingNote.date))
    pagination = query.paginate(page, page_size)
    context = {
        'public_only': True,
        'pagination': pagination,
    }
    return render_template('tasting/list.html', **context)


@tasting_bp.route('/<int:brew_id>/add', methods=['GET', 'POST'], endpoint='add')
@login_required
def brew_add_tasting_note(brew_id):
    brew = Brew.query.get_or_404(brew_id)
    if not brew.has_access(current_user):
        abort(403)
    form = TastingNoteForm()
    if form.validate_on_submit():
        form.save(brew)
        flash(_('tasting note for %(brew)s saved', brew=brew.name), category='success')
        next_ = request.args.get('next') or url_for('brew.details', brew_id=brew.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'form': form,
    }
    return render_template('tasting/tasting_note.html', **ctx)


@tasting_bp.route('/<int:note_id>/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def brew_delete_tasting_note(note_id):
    note = TastingNote.query.get_or_404(note_id)
    if current_user not in (note.author, note.brew.brewery.brewer):
        abort(403)
    brew = note.brew
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        db.session.delete(note)
        db.session.commit()
        flash(_('tasting note for brew %(brew)s has been deleted', brew=brew.name), category='success')
        next_ = request.args.get('next') or url_for('brew.details', brew_id=brew.id)
        return redirect(next_)
    ctx = {
        'brew': brew,
        'note': note,
        'delete_form': form,
    }
    return render_template('tasting/tasting_note_delete.html', **ctx)


@tasting_bp.route('/ajaxtext', endpoint='loadtext')
def brew_load_tasting_note_text():
    provided_id = request.args.get('id')
    if not provided_id:
        abort(400)
    note_id = provided_id.rsplit('_', 1)[-1]
    note = TastingNote.query.get(note_id)
    if note is None:
        abort(404)
    return note.text


@tasting_bp.route('/ajaxupdate', methods=['POST'], endpoint='update')
@login_required
def brew_update_tasting_note():
    note_id = request.form.get('pk')
    if not note_id:
        abort(400)
    note = TastingNote.query.get(note_id)
    if note is None:
        abort(404)
    if current_user not in (note.author, note.brew.brewery.brewer) or not note.brew.has_access(current_user):
        abort(403)
    value = request.form.get('value', '').strip()
    if value:
        note.text = value
        db.session.add(note)
        db.session.commit()
        return markdown.markdown(value, safe_mode='remove')
    return note.text_html
