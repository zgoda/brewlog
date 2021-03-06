from flask import Response, flash, redirect, session, url_for
from flask_babel import lazy_gettext as _
from flask_login import login_user

from ..ext import db
from ..models import BrewerProfile
from ..utils.views import next_redirect


def login_success(
            email: str, access_token: str, remote_id: str, service_name: str, **kwargs
        ) -> Response:
    user = BrewerProfile.get_by_email(email)
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
    flash(
        _(
            'You have been signed in as %(email)s using %(service)s', email=email,
            service=service_name
        ),
        category='success'
    )
    if user.has_valid_password:
        next_ = next_redirect('home.index')
    else:
        next_ = url_for('profile.setpassword')
    return redirect(next_)
