from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, logout_user
from itsdangerous.url_safe import URLSafeTimedSerializer

from ..brew.utils import BrewUtils
from ..ext import db
from ..models import Brew, BrewerProfile, Brewery
from ..tasks import send_email
from ..utils.forms import DeleteForm
from ..utils.pagination import get_page
from ..utils.views import check_token
from . import profile_bp
from .forms import ConfirmBeginForm, PasswordChangeForm, ProfileForm
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
        'profile': user_profile,
        'latest_brews': Brew.get_latest_for(user_profile, limit=10),
    }
    if user_profile == current_user:
        context['form'] = form or ProfileForm(obj=user_profile)
    return render_template('account/profile.html', **context)


@profile_bp.route('/newpassword', methods=['GET', 'POST'], endpoint='setpassword')
@login_required
def set_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        user = form.save(current_user)
        flash(_('your password has been changed'), category='success')
        return redirect(url_for('.details', user_id=user.id))
    context = {
        'form': form,
    }
    return render_template('account/set_password.html', **context)


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


@profile_bp.route(
    '/email/confirm', methods=['POST', 'GET'], endpoint='email-confirm-begin'
)
@login_required
def email_confirmation_begin():
    if request.method == 'POST':
        if not current_user.email:
            abort(400)
        payload = {'id': current_user.id}
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(payload)
        html_body = render_template('email/email_confirmation.html', token=token)
        subject = _('Email confirmation at Brewlog')
        send_email(
            current_app.config['EMAIL_SENDER'], [current_user.email], subject, html_body
        )
        flash(
            _(
                'confirmation email has been sent to %(email)s, please check your '
                'mailbox',
                email=current_user.email,
            ),
            category='success',
        )
        return redirect(url_for('.details', user_id=current_user.id))
    return render_template('account/email_confirm_begin.html', form=ConfirmBeginForm())


@profile_bp.route('/email/confirm/<token>', endpoint='email-confirm-token')
@login_required
def email_confirm(token: str):
    check_result = check_token(
        token, current_app.config['SECRET_KEY'],
        current_app.config['EMAIL_CONFIRM_MAX_AGE'],
    )
    msg = check_result.message
    if not check_result.is_error:
        if check_result.payload['id'] != current_user.id:
            abort(400)
        current_user.set_email_confirmed()
        db.session.add(current_user)
        db.session.commit()
        msg = _('your email has been confirmed succesfully')
        category = 'success'
    else:
        category = 'danger'
    flash(msg, category=category)
    return redirect(url_for('.details', user_id=current_user.id))
