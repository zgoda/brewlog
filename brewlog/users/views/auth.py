import requests
from flask import render_template, redirect, url_for, session, flash, request
from flask_babel import gettext as _
from flask_login import login_user, logout_user, login_required

from brewlog.db import session as dbsession
from brewlog.users.auth import services, google, facebook
from brewlog.models.users import BrewerProfile


def select_provider():
    session['next'] = request.args.get('next')
    return render_template('auth/select.html')

def remote_login(provider):
    if services.get(provider) is None:
        flash(_('Service "%(provider)s" is not supported', provider=provider))
        return redirect(url_for('auth-select-provider'))
    view_name = 'auth-callback-%s' % provider
    callback = url_for(view_name, _external=True)
    service = services[provider][0]
    if provider == 'local':
        return local_login_callback(request.args.get('email', None))
    return service.authorize(callback=callback)

@google.authorized_handler
def google_remote_login_callback(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    if access_token:
        headers = {
            'Authorization': 'OAuth %s' % access_token,
        }
        r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
        if r.ok:
            data = r.json()
            user = BrewerProfile.query.filter_by(email=data['email']).first()
            if user is None:
                user = BrewerProfile(email=data['email'])
            user.access_token = access_token
            user.remote_userid = data['id']
            user.oauth_service = 'google'
            dbsession.add(user)
            dbsession.commit()
            login_user(user)
            session.permanent = True
            flash(_('You have been signed in as %(email)s using Google', email=data['email']))
            next_ = request.args.get('next') or session.pop('next', None) or url_for('profile-details', userid=user.id)
            return redirect(next_)
        else:
            flash(_('Error receiving profile data from Google: %(code)s', code=r.status_code))
    return redirect(url_for('auth-select-provider'))

@facebook.authorized_handler
def facebook_remote_login_callback(resp):
    if resp is None:
        flash(_('Facebook login error, reason: %(error_reason)s, description: %(error_description)s', **request.args))
        return redirect(url_for('auth-select-provider'))
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    if access_token:
        me = facebook.get('/me')
        user = BrewerProfile.query.filter_by(email=me.data['email']).first()
        if user is None:
            user = BrewerProfile(
                email=me.data['email'],
                first_name=me.data['first_name'],
                last_name=me.data['last_name'],
            )
        user.access_token = access_token
        user.oauth_service = 'facebook'
        user.remote_userid = me.data['id']
        dbsession.add(user)
        dbsession.commit()
        login_user(user)
        session.permanent = True
        flash(_('You have been signed in as %(email)s using Facebook', email=me.data['email']))
        next_ = request.args.get('next') or session.pop('next', None) or url_for('profile-details', userid=user.id)
        return redirect(next_)
    return redirect(url_for('auth-select-provider'))

def local_login_callback(resp):
    if resp is not None:
        email = resp
    else:
        email = 'user@example.com'
    user = BrewerProfile.query.filter_by(email=email).first()
    if user is None:
        user = BrewerProfile(email=email, nick='example user')
        dbsession.add(user)
        dbsession.commit()
    login_user(user)
    session.permanent = True
    flash(_('You have been signed in as %(email)s using local handler', email=email))
    next_ = request.args.get('next') or session.pop('next', None) or url_for('profile-details', userid=user.id)
    return redirect(next_)

@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))
