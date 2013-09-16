from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from flask_babel import gettext as _
from sqlalchemy import desc

from brewlog.utils.models import get_or_404, Pagination, paginate
from brewlog.models import BrewerProfile, Brewery, Brew
from brewlog.users.forms import ProfileForm
from brewlog.brewing.forms.brew import BrewDeleteForm


def profile(userid, **kwargs):
    user_profile = get_or_404(BrewerProfile, userid)
    if request.method == 'POST':
        if current_user != user_profile:
            abort(403)
        form = ProfileForm(request.form)
        if form.validate():
            form.save(obj=user_profile)
            flash(_('your profile data has been updated'))
            next_ = request.args.get('next')
            if next_ is None:
                next_ = url_for('profile-details', userid=userid)
                return redirect(next_)
            else:
                return redirect(url_for(next_))
    context = {
        'data': user_profile.summary_data(['nick']),
        'data_type': 'summary',
        'profile': user_profile,
    }
    if user_profile.has_access(current_user):
        context['data'] = user_profile.full_data()
        context['data_type'] = 'full'
    else:        
        abort(404)
    if user_profile == current_user:
        context['form'] = ProfileForm(obj=user_profile)
    return render_template('account/profile.html', **context)

def profile_list():
    page_size = 20
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    query = BrewerProfile.query.filter_by(is_public=True).order_by(BrewerProfile.created)
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'users': paginate(query, page-1, page_size),
        'pagination': pagination,
    }
    return render_template('account/profile_list.html', **ctx)

def breweries(userid):
    brewer = BrewerProfile.query.get(userid)
    if not brewer or (not brewer.is_public and current_user.id != userid):
        abort(404)
    page_size = 10
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    query = Brewery.query.filter_by(brewer_id=userid).order_by(Brewery.name)
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'breweries': paginate(query, page-1, page_size),
        'pagination': pagination,
    }
    return render_template('brewery/list.html', **ctx)

def brews(userid):
    brewer = BrewerProfile.query.get(userid)
    if not brewer or (not brewer.is_public and current_user.id != userid):
        abort(404)
    page_size = 10
    try:
        page = int(request.args.get('p', '1'))
    except ValueError:
        page = 1
    query = Brew.query.join(Brewery).filter(Brewery.brewer_id==userid)
    if current_user.id != userid:
        query = query.filter_by(is_public=True)
    query = query.order_by(desc(Brew.created))
    pagination = Pagination(page, page_size, query.count())
    ctx = {
        'brews': paginate(query, page-1, page_size),
        'pagination': pagination,
        'delete_form': BrewDeleteForm(),
    }
    return render_template('brew/list.html', **ctx)
