# Copyright 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask import flash, redirect, session
from flask_babel import lazy_gettext as _
from flask_login import login_user

from ..ext import db
from ..models import BrewerProfile
from ..utils.views import next_redirect


def login_success(email, access_token, remote_id, service_name, **kwargs):
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
    next_ = next_redirect('home.index')
    return redirect(next_)
