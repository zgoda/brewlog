from flask import redirect, url_for, session, flash, request
from flask.ext.babel import gettext as _
from flask.ext.login import login_user

import brewlog.models.calendar  # NOQA
from brewlog.models.users import BrewerProfile
from brewlog.db import session as dbsession


def login_success(email, access_token, remote_id, service_name, **kwargs):
    user = BrewerProfile.query.filter_by(email=email).first()
    if user is None:
        user = BrewerProfile(email=email)
    user.access_token = access_token
    user.remote_userid = remote_id
    user.oauth_service = service_name
    for k, v in kwargs.items():
        setattr(user, k, v)
    dbsession.add(user)
    dbsession.commit()
    login_user(user)
    session.permanent = True
    flash(_('You have been signed in as %(email)s using %(service)s', email=email, service=service_name),
        category='success')
    next_ = request.args.get('next') or session.pop('next', None) or url_for('profile-details', userid=user.id)
    return redirect(next_)
