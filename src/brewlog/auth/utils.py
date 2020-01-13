import os

from flask import (
    Response, current_app, flash, redirect, render_template_string, session, url_for,
)
from flask_babel import lazy_gettext as _
from flask_login import login_user
from itsdangerous.url_safe import URLSafeTimedSerializer

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


def send_password_reset_email(email: str) -> bool:
    user = BrewerProfile.get_by_email(email)
    if user is not None and user.email_confirmed:
        payload = {'id': user.id}
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(payload)
        html_body = render_template_string('email/password_reset.html', token=token)
        queue = current_app.queues['mail']
        mg_domain = os.environ['MAILGUN_DOMAIN']
        subject = _('Request to reset password at Brewlog')
        queue.enqueue(
            'brewlog.tasks.send_email', f'brewlog@{mg_domain}', [user.email],
            subject, html_body,
        )
        return True
    return False


def decode_token(token: str):
    pass
