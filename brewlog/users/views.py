import requests
from flask import render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required

from brewlog.users.auth import services, google
from brewlog.users.models import BrewerProfile


def select_provider():
    return render_template('auth/select.html')

def remote_login(provider):
    if services.get(provider) is None:
        return redirect(url_for('auth-select-provider'))
    callback = url_for('auth-callback', provider=provider, _external=True)
    service = services[provider]
    return service.authorize(callback=callback)

@google.authorized_handler
def remote_login_callback(resp, provider):
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
            login_user(user)
            next_url = session.get('next') or url_for('main')
            return redirect(next_url)
    return redirect(url_for('auth-select-provider'))

@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

def profile():
    return render_template('account/profile.html')

def dashboard():
    return render_template('account/profile.html')
