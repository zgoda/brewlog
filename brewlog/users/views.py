import requests
from flask import render_template, redirect, url_for, session, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from flaskext.babel import lazy_gettext as _

from brewlog import session as dbsession
from brewlog.users.auth import services, google, facebook
from brewlog.users.models import BrewerProfile
from brewlog.users.forms import ProfileForm


def select_provider():
    return render_template('auth/select.html')

def remote_login(provider):
    if services.get(provider) is None:
        return redirect(url_for('auth-select-provider'))
    view_name = 'auth-callback-%s' % provider
    callback = url_for(view_name, _external=True)
    service = services[provider][0]
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
            next_url = request.args.get('next') or session.get('next') or 'main'
            flash(_('You have been signed in as %(email)s using Google', email=data['email']))
            return redirect(url_for(next_url))
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
        next_url = request.args.get('next') or session.get('next') or 'main'
        flash(_('You have been signed in as %(email)s using Facebook', email=me.data['email']))
        return redirect(url_for(next_url))
    return redirect(url_for('auth-select-provider'))

@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

def profile():
    return render_template('account/profile.html')

@login_required
def dashboard(userid):
    if str(userid) != str(current_user.id):
        abort(403)
    if request.method == 'POST':
        form = ProfileForm(request.form)
        if form.validate():
            form.save(obj=current_user)
            flash(_('your profile data has been updated'))
            next_ = request.args.get('next')
            if next_ is None:
                next_ = url_for('profile-details', userid=userid)
                return redirect(next_)
            else:
                return redirect(url_for(next_))
    form = ProfileForm(obj=current_user)
    context = {
        'form': form,
    }
    return render_template('account/profile.html', **context)
