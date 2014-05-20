import requests
from flask import render_template, redirect, url_for, session, flash, request
from flask.ext.babel import gettext as _
from flask.ext.login import logout_user, login_required

from brewlog.users.auth import services, google, facebook, github
from brewlog.users.utils import login_success


def select_provider():  # pragma: no cover
    session['next'] = request.args.get('next')
    return render_template('auth/select.html')


def remote_login(provider):
    if services.get(provider) is None:
        flash(_('Service "%(provider)s" is not supported', provider=provider), category='error')
        return redirect(url_for('auth-select-provider'))
    view_name = 'auth-callback-%s' % provider
    callback = url_for(view_name, _external=True)
    service = services[provider][0]
    if provider == 'local':
        return local_login_callback(request.args.get('email', None))
    return service.authorize(callback=callback)  # pragma: no cover


@google.authorized_handler
def google_remote_login_callback(resp):  # pragma: no cover
    access_token = resp.get('access_token')
    if access_token:
        session['access_token'] = access_token, ''
        headers = {
            'Authorization': 'OAuth %s' % access_token,
        }
        r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
        if r.ok:
            data = r.json()
            return login_success(data['email'], access_token, data['id'], 'google')
        else:
            flash(_('Error receiving profile data from Google: %(code)s', code=r.status_code), category='error')
    return redirect(url_for('auth-select-provider'))


@facebook.authorized_handler
def facebook_remote_login_callback(resp):  # pragma: no cover
    if resp is None:
        flash(_('Facebook login error, reason: %(error_reason)s, description: %(error_description)s', **request.args),
            category='error')
        return redirect(url_for('auth-select-provider'))
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    if access_token:
        me = facebook.get('/me')
        kw = {
            'first_name': me.data['first_name'],
            'last_name': me.data['last_name'],
        }
        return login_success(me.data['email'], access_token, me.data['id'], 'facebook', **kw)
    return redirect(url_for('auth-select-provider'))


@github.authorized_handler
def github_remote_login_callback(resp):  # pragma: no cover
    skip = redirect(url_for('auth-select-provider'))
    if resp is None:
        flash(_('GitHub login error, reason: %(error)s, description: %(error_description)s', **request.args),
            category='error')
        return skip
    access_token = resp.get('access_token')
    if access_token is None:
        flash(_('GitHub login error, reason: %(error)s, description: %(error_description)s', **resp),
            category='error')
        return skip
    session['access_token'] = access_token, ''
    if access_token:
        me = github.get('user')
        if not me.data.get('email'):
            flash(_('GitHub profile for user %(name)s lacks public email, skipping as unusable.', **me.data),
                category='warning')
            return skip
        return login_success(me.data['email'], access_token, me.data['id'], 'github')
    return skip


def local_login_callback(resp):
    if resp is not None:
        email = resp
    else:
        email = 'user@example.com'
    return login_success(email, 'dummy', 'dummy', 'local handler', nick='example user')


@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))
