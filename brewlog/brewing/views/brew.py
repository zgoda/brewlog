from flask import request, flash, url_for, redirect, render_template, abort, render_template_string
from flask_login import current_user, login_required
from flask_babel import gettext as _
from flask_babel import lazy_gettext
from sqlalchemy import desc
import markdown

from brewlog.db import session as dbsession
from brewlog.models import brews
from brewlog.models.brewing import Brew, TastingNote
from brewlog.models.users import CustomLabelTemplate
from brewlog.forms.base import DeleteForm
from brewlog.utils.models import get_or_404, Pagination, paginate
from brewlog.brewing.forms.brew import BrewForm, TastingNoteForm


HINTS = [
    ("67-66*C - 90'\n75*C - 15'", lazy_gettext('single infusion mash w/ mash out')),
    ("63-61*C - 30'\n73-71*C - 30'\n75*C - 15'", lazy_gettext('2-step mash w/ mash out')),
    ("55-54*C - 10'\n63-61*C - 30'\n73-71*C - 30'\n75*C - 15'", lazy_gettext('3-step mash w/ mash out')),
]


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
        'notes': brew.notes_to_json(),
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
        query = brews()
    else:
        query = brews(extra_user=current_user)
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
        'custom_templates': [],
        'rendered_cell': None,
        'rows': 5,
        'cols': 2,
        'cell_style': 'width:90mm;height:50mm',
        'current_template': 0,
    }
    if current_user.is_authenticated():
        ctx['custom_templates'] = current_user.custom_label_templates.order_by(CustomLabelTemplate.name).all()
    use_template = request.args.get('template')
    if use_template is not None:
        template_obj = current_user.custom_label_templates.filter_by(id=use_template).one()
        if template_obj is not None:
            custom_data = dict(
                rendered_cell = render_template_string(markdown.markdown(template_obj.text, safe_mode='remove'), brew=brew),
                rows = template_obj.rows,
                cols = template_obj.cols,
                cell_style = 'width:%smm;height:%smm' % (template_obj.width, template_obj.height),
                current_template = template_obj.id,
            )
            ctx.update(custom_data)
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
