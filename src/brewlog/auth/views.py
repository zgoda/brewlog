# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import flash, redirect, render_template, request, session, url_for
from flask_babel import gettext as _
from flask_login import login_required, logout_user

from . import auth_bp
from . import providers
from ..ext import oauth
from .utils import login_success


@auth_bp.route('/select', endpoint='select')
def select_provider():
    session['next'] = request.args.get('next')
    return render_template('auth/select.html')


@auth_bp.route('/<provider>', endpoint='login')
def remote_login(provider):
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
        else:
            flash(
                _(
                    'Error receiving profile data from Google: %(code)s',
                    code=r.status_code,
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
def logout():
    logout_user()
    return redirect(url_for('home.index'))
