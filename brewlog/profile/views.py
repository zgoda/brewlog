from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, logout_user

from . import profile_bp
from ..brew.utils import BrewUtils
from ..ext import db
from ..forms.base import DeleteForm
from ..models import (
    Brew, BrewerProfile, Brewery, CustomExportTemplate, CustomLabelTemplate,
)
from ..profile.forms import (
    CustomExportTemplateForm, CustomLabelTemplateForm, ProfileForm,
)
from ..utils.pagination import get_page
from ..utils.views import get_user_object


@profile_bp.route('/<int:userid>', methods=['GET', 'POST'], endpoint='details')
def profile(userid, **kwargs):
    user_profile = BrewerProfile.query.get_or_404(userid)
    if not user_profile.has_access(current_user):
        abort(404)
    if request.method == 'POST' and current_user != user_profile:
        abort(403)
    form = ProfileForm()
    if form.validate_on_submit():
        profile = form.save(obj=user_profile)
        flash(_('your profile data has been updated'), category='success')
        return redirect(profile.absolute_url)
    context = {
        'data': user_profile.nick,
        'data_type': 'summary',
        'profile': user_profile,
        'latest_brews': Brew.get_latest_for(user_profile),
    }
    context['data'] = user_profile.full_data()
    context['data_type'] = 'full'
    if user_profile == current_user:
        context['form'] = ProfileForm(obj=user_profile)
    return render_template('account/profile.html', **context)


@profile_bp.route('<int:userid>/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def profile_delete(userid):
    profile = BrewerProfile.query.get_or_404(userid)
    if current_user != profile:
        abort(403)
    email = profile.email
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        logout_user()
        db.session.delete(profile)
        db.session.commit()
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
    query = BrewerProfile.public(order_by=BrewerProfile.created)
    pagination = query.paginate(page, page_size)
    ctx = {
        'pagination': pagination,
    }
    return render_template('account/profile_list.html', **ctx)


@profile_bp.route('/<int:userid>/breweries', endpoint='breweries')
def breweries(userid):
    brewer = BrewerProfile.query.get_or_404(userid)
    if current_user != brewer and not brewer.is_public:
        abort(404)
    page_size = 10
    page = get_page(request)
    query = brewer.breweries.order_by(Brewery.name)
    pagination = query.paginate(page, page_size)
    ctx = {
        'pagination': pagination,
    }
    return render_template('brewery/list.html', **ctx)


@profile_bp.route('/<int:userid>/brews', endpoint='brews')
def brews(userid):
    brewer = BrewerProfile.query.get_or_404(userid)
    if current_user != brewer and not brewer.is_public:
        abort(404)
    page_size = 10
    page = get_page(request)
    query = Brew.query.join(Brewery).filter(Brewery.brewer_id == userid)
    if current_user.is_anonymous or current_user.id != userid:
        query = query.filter(Brew.is_public.is_(True))
    query = query.order_by(db.desc(Brew.created))
    pagination = query.paginate(page, page_size)
    ctx = {
        'pagination': pagination,
        'utils': BrewUtils,
    }
    return render_template('brew/list.html', **ctx)


@profile_bp.route(
    '/<int:userid>/extemplate',
    methods=['GET', 'POST'], defaults={'tid': None},
    endpoint='export_template_add'
)
@profile_bp.route(
    '/<int:userid>/extemplate/<int:tid>',
    methods=['GET', 'POST'],
    endpoint='export_template'
)
@login_required
def export_template(userid, tid=None):
    template = get_user_object(CustomExportTemplate, tid)
    form = CustomExportTemplateForm()
    if form.validate_on_submit():
        return form.save_and_redirect(current_user, template)
    form = CustomExportTemplateForm(obj=template)
    ctx = {
        'form': form,
        'template': template,
    }
    return render_template('account/export_template.html', **ctx)


@profile_bp.route(
    '/<int:userid>/lbtemplate',
    methods=['GET', 'POST'], defaults={'tid': None},
    endpoint='label_template_add'
)
@profile_bp.route(
    '/<int:userid>/lbtemplate/<int:tid>',
    methods=['GET', 'POST'],
    endpoint='label_template'
)
@login_required
def label_template(userid, tid=None):
    template = get_user_object(CustomLabelTemplate, tid)
    form = CustomLabelTemplateForm()
    if form.validate_on_submit():
        return form.save_and_redirect(current_user, template)
    form = CustomLabelTemplateForm(obj=template)
    ctx = {
        'form': form,
        'template': template,
    }
    return render_template('account/label_template.html', **ctx)
