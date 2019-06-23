# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, logout_user

from ..brew.utils import BrewUtils
from ..ext import db
from ..forms.base import DeleteForm
from ..models import Brew, BrewerProfile, Brewery
from ..utils.pagination import get_page
from . import profile_bp
from .forms import ProfileForm
from .permissions import AccessManager


@profile_bp.route('/<int:user_id>', methods=['GET', 'POST'], endpoint='details')
def profile(user_id):
    user_profile = BrewerProfile.query.get_or_404(user_id)
    is_post = request.method == 'POST'
    AccessManager(user_profile, is_post).check()
    form = None
    if is_post:
        form = ProfileForm()
        if form.validate_on_submit():
            profile = form.save(obj=user_profile)
            flash(_('your profile data has been updated'), category='success')
            return redirect(url_for('.details', user_id=profile.id))
    context = {
        'data': user_profile.nick,
        'data_type': 'summary',
        'profile': user_profile,
        'latest_brews': Brew.get_latest_for(user_profile, limit=10),
    }
    context['data'] = user_profile.full_data()
    context['data_type'] = 'full'
    if user_profile == current_user:
        context['form'] = form or ProfileForm(obj=user_profile)
    return render_template('account/profile.html', **context)


@profile_bp.route('<int:user_id>/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def profile_delete(user_id):
    profile = BrewerProfile.query.get_or_404(user_id)
    AccessManager(profile, True).check()
    email = profile.email
    form = DeleteForm()
    if form.validate_on_submit() and form.delete_it.data:
        logout_user()
        db.session.delete(profile)
        db.session.commit()
        flash(
            _('profile for %(email)s has been deleted', email=email), category='success'
        )
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


@profile_bp.route('/<int:user_id>/breweries', endpoint='breweries')
def breweries(user_id):
    brewer = BrewerProfile.query.get_or_404(user_id)
    AccessManager(brewer, False).check()
    page_size = 10
    page = get_page(request)
    query = brewer.breweries.order_by(Brewery.name)
    pagination = query.paginate(page, page_size)
    ctx = {
        'pagination': pagination,
    }
    return render_template('brewery/list.html', **ctx)


@profile_bp.route('/<int:user_id>/brews', endpoint='brews')
def brews(user_id):
    brewer = BrewerProfile.query.get_or_404(user_id)
    AccessManager(brewer, False).check()
    page_size = 10
    page = get_page(request)
    query = Brew.query.join(Brewery).filter(Brewery.brewer_id == user_id)
    if current_user.is_anonymous or current_user.id != user_id:
        query = query.filter(Brew.is_public.is_(True))
    query = query.order_by(db.desc(Brew.created))
    pagination = query.paginate(page, page_size)
    ctx = {
        'pagination': pagination,
        'utils': BrewUtils,
        'user_is_brewer': current_user == brewer,
    }
    return render_template('brew/list.html', **ctx)
