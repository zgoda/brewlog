from flask import redirect, url_for, session, flash, request
from flask_babelex import gettext as _
from flask_login import login_user

from brewlog.models.users import BrewerProfile
from brewlog.ext import db


def login_success(email, access_token, remote_id, service_name, **kwargs):
    user = BrewerProfile.query.filter_by(email=email).first()
    if user is None:
        user = BrewerProfile(email=email)
    user.access_token = access_token
    user.remote_userid = remote_id
    user.oauth_service = service_name
    for k, v in kwargs.items():
        setattr(user, k, v)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    session.permanent = True
    flash(_('You have been signed in as %(email)s using %(service)s', email=email, service=service_name),
        category='success')
    next_ = request.args.get('next') or session.pop('next', None) or url_for('profile.details', userid=user.id)
    return redirect(next_)
