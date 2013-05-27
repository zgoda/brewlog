import requests
from flask import render_template, redirect, url_for, session, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from flaskext.babel import lazy_gettext as _

from brewlog import session as dbsession
from brewlog.utils.models import get_or_404
from brewlog.users.auth import services, google, facebook
from brewlog.models import BrewerProfile
from brewlog.users.forms import ProfileForm


def select_provider():
    return render_template('auth/select.html')

def remote_login(provider):
    if services.get(provider) is None:
        flash(_('Service "%(provider)s" is not supported', provider=provider))
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
        next_url = request.args.get('next') or session.get('next') or 'main'
        flash(_('You have been signed in as %(email)s using Facebook', email=me.data['email']))
        return redirect(url_for(next_url))
    return redirect(url_for('auth-select-provider'))

@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

def profile(userid, **kwargs):
    user_profile = get_or_404(BrewerProfile, userid)
    is_owner = False
    if current_user.is_authenticated():
        is_owner = user_profile.id == current_user.id
    context = {
        'data': user_profile.summary_data(['nick']),
        'data_type': 'summary',
        'user': user_profile,
    }
    if is_owner:
        context['form'] = ProfileForm(obj=current_user)
    if is_owner or (current_user.is_authenticated() and user_profile.is_public):
        context['data'] = user_profile.full_data()
        context['data_type'] = 'full'
    if request.method == 'POST':
        if not is_owner:
            abort(403)
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
    return render_template('account/profile.html', **context)
