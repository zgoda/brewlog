from flask import render_template, redirect, url_for, flash, request, abort
from flask.ext.login import current_user, login_required, logout_user
from flask.ext.babel import gettext as _
from sqlalchemy import desc


from brewlog.db import session as dbsession
from brewlog.utils.models import get_or_404, Pagination, paginate, get_page
from brewlog.models.users import BrewerProfile, CustomExportTemplate, CustomLabelTemplate
from brewlog.models.brewing import Brewery, Brew
from brewlog.models.calendar import Event
from brewlog.profile.forms import ProfileForm, CustomExportTemplateForm, CustomLabelTemplateForm
from brewlog.forms.base import DeleteForm
from brewlog.profile import profile_bp


@profile_bp.route('/<int:userid>', methods=['GET', 'POST'], endpoint='details')
def profile(userid, **kwargs):
    user_profile = get_or_404(BrewerProfile, userid)
    if request.method == 'POST':
        if current_user != user_profile:
            abort(403)
        form = ProfileForm(request.form)
        if form.validate():
            profile = form.save(obj=user_profile)
            flash(_('your profile data has been updated'), category='success')
            return redirect(profile.absolute_url)
    context = {
        'data': user_profile.nick,
        'data_type': 'summary',
        'profile': user_profile,
        'latest_brews': Brew.get_latest_for(user_profile),
        'latest_events': Event.get_latest_for(user_profile),
    }
    if user_profile.has_access(current_user):
        context['data'] = user_profile.full_data()
        context['data_type'] = 'full'
    else:
        abort(404)
    if user_profile == current_user:
        context['form'] = ProfileForm(obj=user_profile)
    return render_template('account/profile.html', **context)


@profile_bp.route('<int:userid>/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def profile_delete(userid):
    profile = get_or_404(BrewerProfile, userid)
    if current_user != profile:
        abort(403)
    email = profile.email
    form = DeleteForm(request.form)
    if request.method == 'POST':
        if form.validate() and form.delete_it.data:
            logout_user()
            dbsession.delete(profile)
            dbsession.commit()
            flash(_('profile for %(email)s has been deleted', email=email), category='success')
            return redirect(url_for('home.index'))
    ctx = {
        'profile': profile,
        'delete_form': form,
    }
    return render_template('account/delete.html', **ctx)


@profile_bp.route('/all', endpoint='all')
def profile_list():
    page_size = 20
    page = get_page(request)
    query = BrewerProfile.query.filter_by(is_public=True).order_by(BrewerProfile.created)
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'users': paginate(query, page-1, page_size),
        'pagination': pagination,
    }
    return render_template('account/profile_list.html', **ctx)


@profile_bp.route('/<int:userid>/breweries', endpoint='breweries')
def breweries(userid):
    brewer = BrewerProfile.query.get(userid)
    if not brewer or (not brewer.is_public and current_user.id != userid):
        abort(404)
    page_size = 10
    page = get_page(request)
    query = Brewery.query.filter_by(brewer_id=userid).order_by(Brewery.name)
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'breweries': paginate(query, page-1, page_size),
        'pagination': pagination,
    }
    return render_template('brewery/list.html', **ctx)


@profile_bp.route('/<int:userid>/brews', endpoint='brews')
def brews(userid):
    brewer = BrewerProfile.query.get(userid)
    if not brewer or (not brewer.is_public and current_user.id != userid):
        abort(404)
    page_size = 10
    page = get_page(request)
    query = Brew.query.join(Brewery).filter(Brewery.brewer_id==userid)
    if current_user.is_anonymous() or current_user.id != userid:
        query = query.filter(Brew.is_public==True)
    query = query.order_by(desc(Brew.created))
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'brews': paginate(query, page-1, page_size),
        'pagination': pagination,
    }
    return render_template('brew/list.html', **ctx)


@profile_bp.route('/<int:userid>/extemplate', methods=['GET', 'POST'], defaults={'tid': None}, endpoint='export_template_add')  # noqa
@profile_bp.route('/<int:userid>/extemplate/<int:tid>', methods=['GET', 'POST'], endpoint='export_template')
@login_required
def export_template(userid, tid=None):
    template = None
    if tid is not None:
        template = get_or_404(CustomExportTemplate, tid)
        if template.user != current_user:
            abort(403)
    if request.method == 'POST':
        form = CustomExportTemplateForm(request.form)
        if form.validate():
            template = form.save(current_user, template)
            flash(_('your export template %(name)s has been saved', name=template.name), category='success')
            return redirect(template.absolute_url)
    form = CustomExportTemplateForm(obj=template)
    ctx = {
        'form': form,
        'template': template,
    }
    return render_template('account/export_template.html', **ctx)

@profile_bp.route('/<int:userid>/lbtemplate', methods=['GET', 'POST'], defaults={'tid': None}, endpoint='label_template_add')  # noqa
@profile_bp.route('/<int:userid>/lbtemplate/<int:tid>', methods=['GET', 'POST'], endpoint='label_template')
@login_required
def label_template(userid, tid=None):
    template = None
    if tid is not None:
        template = get_or_404(CustomLabelTemplate, tid)
        if template.user != current_user:
            abort(403)
    if request.method == 'POST':
        form = CustomLabelTemplateForm(request.form)
        if form.validate():
            template = form.save(current_user, template)
            flash(_('your label template %(name)s has been saved', name=template.name), category='success')
            next_ = url_for('profile.details', userid=current_user.id)
            return redirect(next_)
    form = CustomLabelTemplateForm(obj=template)
    ctx = {
        'form': form,
        'template': template,
    }
    return render_template('account/label_template.html', **ctx)
