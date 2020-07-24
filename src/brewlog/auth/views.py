from typing import Union

from flask import (
    Response, abort, current_app, flash, redirect, render_template, request, session,
    url_for,
)
from flask_babel import gettext as _
from flask_login import login_required, logout_user

from ..models import BrewerProfile
from ..profile.forms import PasswordChangeForm
from ..utils.views import check_token, next_redirect
from . import auth_bp
from .forms import ForgotPassword, LoginForm, RegistrationForm


@auth_bp.route('/register', methods=['POST', 'GET'])
def register() -> Union[str, Response]:
    logout_user()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.save()
        flash(
            _(
                'account for %(user)s has been created, you may proceed to login',
                user=user.username,
            ),
            category='success',
        )
        return redirect(url_for('auth.select'))
    ctx = {
        'form': form,
    }
    return render_template('auth/register.html', **ctx)


@auth_bp.route('/password/forgot', methods=['POST', 'GET'], endpoint='forgotpassword')
def forgot_password() -> Union[str, Response]:
    form = ForgotPassword()
    if form.validate_on_submit():
        if form.save():
            msg = _(
                'message with password reset instructions has been sent to specified '
                'email'
            ), 'success'
        else:
            msg = _(
                "something went wrong, either we don't know that email or it's not yet "
                "confirmed"
            ), 'warning'
        msg, category = msg
        flash(msg, category=category)
        return redirect(next_redirect('home.index'))
    ctx = {
        'form': form,
    }
    return render_template('auth/forgotpassword.html', **ctx)


@auth_bp.route(
    '/password/reset/<token>', methods=['POST', 'GET'], endpoint='resetpassword'
)
def reset_password(token: str) -> Union[str, Response]:
    check_result = check_token(
        token, current_app.config['SECRET_KEY'],
        current_app.config['PASSWORD_RESET_MAX_AGE'],
    )
    if check_result.is_error:
        flash(check_result.message, category='danger')
        return redirect(url_for('auth.select'))
    user = BrewerProfile.query.get(check_result.payload['id'])
    if not user:
        abort(400)
    form = PasswordChangeForm()
    if form.validate_on_submit():
        form.save(user)
        flash(_('your password has been changed'), category='success')
        return redirect(url_for('.select'))
    ctx = {
        'form': form
    }
    return render_template('account/set_password.html', **ctx)


@auth_bp.route('/select', methods=['POST', 'GET'], endpoint='select')
def select_provider() -> Union[str, Response]:
    session['next'] = request.args.get('next')
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = form.save()
            flash(
                _('you are now logged in as %(name)s', name=user.name),
                category='success',
            )
            return redirect(next_redirect('home.index'))
        flash(_('user account not found or wrong password'), category='danger')
        return redirect(request.path)
    ctx = {
        'form': form,
    }
    return render_template('auth/select.html', **ctx)


@auth_bp.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for('home.index'))
