from typing import Union

from flask import (
    Response, abort, current_app, flash, redirect, render_template, request, session,
    url_for,
)
from flask_babel import gettext as _
from flask_login import login_required, logout_user

from ..ext import oauth
from ..models import BrewerProfile
from ..profile.forms import PasswordChangeForm
from ..utils.views import check_token, next_redirect
from . import auth_bp, providers
from .forms import ForgotPassword, LoginForm, RegistrationForm
from .utils import login_success


@auth_bp.route('/register', methods=['POST', 'GET'], endpoint='register')
def register() -> Union[str, Response]:
    logout_user()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.save()
        flash(
            _(
                'account for %(user)s has been created, you may proceed to login',
                user=user.username,
            ),
            category='success',
        )
        return redirect(url_for('auth.select'))
    ctx = {
        'form': form,
    }
    return render_template('auth/register.html', **ctx)


@auth_bp.route('/password/forgot', methods=['POST', 'GET'], endpoint='forgotpassword')
def forgot_password() -> Union[str, Response]:
    form = ForgotPassword()
    if form.validate_on_submit():
        if form.save():
            msg = _(
                'message with password reset instructions has been sent to specified '
                'email'
            ), 'success'
        else:
            msg = _(
                "something went wrong, either we don't know that email or it's not yet "
                "confirmed"
            ), 'warning'
        msg, category = msg
        flash(msg, category=category)
        return redirect(next_redirect('home.index'))
    ctx = {
        'form': form,
    }
    return render_template('auth/forgotpassword.html', **ctx)


@auth_bp.route(
    '/password/reset/<token>', methods=['POST', 'GET'], endpoint='resetpassword'
)
def reset_password(token: str) -> Union[str, Response]:
    check_result = check_token(
        token, current_app.config['SECRET_KEY'],
        current_app.config['PASSWORD_RESET_MAX_AGE'],
    )
    if check_result.is_error:
        flash(check_result.message, category='danger')
        return redirect(url_for('auth.select'))
    user = BrewerProfile.query.get(check_result.payload['id'])
    if not user:
        abort(400)
    form = PasswordChangeForm()
    if form.validate_on_submit():
        form.save(user)
        flash(_('your password has been changed'), category='success')
        return redirect(url_for('.select'))
    ctx = {
        'form': form
    }
    return render_template('account/set_password.html', **ctx)


@auth_bp.route('/select', methods=['POST', 'GET'], endpoint='select')
def select_provider() -> Union[str, Response]:
    session['next'] = request.args.get('next')
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = form.save()
            flash(
                _('you are now logged in as %(name)s', name=user.name),
                category='success',
            )
            return redirect(next_redirect('home.index'))
        flash(_('user account not found or wrong password'), category='danger')
        return redirect(request.path)
    ctx = {
        'form': form,
    }
    return render_template('auth/select.html', **ctx)


@auth_bp.route('/<provider>', endpoint='login')
def remote_login(provider: str) -> Union[str, Response]:
    if provider == 'local':
        return local_login_callback(
            request.args.get('email', 'example.user@example.com')
        )
    svc = getattr(providers, provider, None)
    if svc is None:
        flash(
            _('Service "%(provider)s" is not supported', provider=provider),
            category='error'
        )
        return redirect(url_for('auth.select'))
    view_name = f'auth.callback-{provider}'
    callback = url_for(view_name, _external=True)
    return svc.authorize_redirect(callback)


@auth_bp.route('/google/callback', endpoint='callback-google')
def google_remote_login_callback():  # pragma: nocover
    resp = oauth.google.authorize_access_token()
    if resp:
        session['access_token'] = resp['access_token'], ''
        r = oauth.google.get('oauth2/v3/userinfo')
        if r.ok:
            data = r.json()
            kw = {
                'first_name': data.get('given_name', ''),
                'last_name': data.get('family_name', ''),
            }
            user_id = data.pop('sub')
            return login_success(
                data['email'], resp['access_token'], user_id, 'google', **kw
            )
    flash(
        _(
            'Error receiving profile data from Google: %(code)s', code=r.status_code,
        ),
        category='error'
    )
    return redirect(url_for('auth.select'))


@auth_bp.route('/facebook/callback', endpoint='callback-facebook')
def facebook_remote_login_callback():  # pragma: nocover
    access_token = oauth.facebook.authorize_access_token()
    session['access_token'] = access_token, ''
    if access_token:
        r = oauth.facebook.get(
            '/me', params={'fields': 'id,email,first_name,last_name'}
        )
        if r.ok:
            data = r.json()
            kw = {
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
            }
            return login_success(
                data['email'], access_token.get('access_token'), data['id'],
                'facebook', **kw,
            )
    return redirect(url_for('auth.select'))


@auth_bp.route('/github/callback', endpoint='callback-github')
def github_remote_login_callback():  # pragma: nocover
    skip = redirect(url_for('auth.select'))
    access_token = oauth.github.authorize_access_token()
    session['access_token'] = access_token, ''
    if access_token:
        r = oauth.github.get('/user')
        if r.ok:
            data = r.json()
            if not data.get('email'):
                flash(
                    _(
                        'GitHub profile for user %(name)s lacks public email, '
                        'skipping as unusable.',
                        **data
                    ),
                    category='warning',
                )
                return skip
            return login_success(
                data['email'], access_token.get('access_token'), data['id'], 'github'
            )
    return skip


@auth_bp.route('/local/callback', endpoint='callback-local')
def local_login_callback(resp):
    return login_success(resp, 'dummy', 'dummy', 'local handler', nick='example user')


@auth_bp.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for('home.index'))
