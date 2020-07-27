from flask import current_app, render_template, session
from flask_login import login_user
from itsdangerous.url_safe import URLSafeTimedSerializer
from wtforms.fields import Field, PasswordField, StringField
from wtforms.validators import EqualTo, InputRequired, ValidationError

from ..ext import db
from ..models.users import BrewerProfile
from ..tasks import send_email
from ..utils.forms import BaseForm, Button, Email


def _rkw(**extra: str) -> dict:
    render_kw = {
        'class_': 'input',
    }
    render_kw.update(extra)
    return render_kw


class RegistrationForm(BaseForm):
    username = StringField('nazwa', validators=[InputRequired()])
    password1 = PasswordField('hasło', validators=[InputRequired()])
    password2 = PasswordField(
        'hasło (powtórz)', validators=[InputRequired(), EqualTo('password1')]
    )

    buttons = [
        Button(icon='user', text='zapisz')
    ]

    def validate_username(self, field: Field):
        if BrewerProfile.query.filter_by(username=field.data).count() > 0:
            raise ValidationError('nazwa użytkownika jest już zajęta')

    def save(self) -> BrewerProfile:
        user = BrewerProfile(username=self.username.data)
        user.set_password(self.password1.data)
        db.session.add(user)
        db.session.commit()
        return user


class LoginForm(BaseForm):
    userid = StringField(
        validators=[InputRequired()],
        render_kw=_rkw(placeholder='email lub login'),
    )
    password = PasswordField(
        validators=[InputRequired()], render_kw=_rkw(placeholder='hasło'),
    )

    def validate(self) -> bool:
        is_valid = super().validate()
        user_found = password_valid = False
        if is_valid:
            self.user = BrewerProfile.query.filter(
                db.or_(
                    BrewerProfile.email == self.userid.data,
                    BrewerProfile.username == self.userid.data,
                )
            ).first()
            user_found = self.user is not None
            if user_found:
                password_valid = self.user.check_password(self.password.data)
        return is_valid and user_found and password_valid

    def save(self) -> BrewerProfile:
        login_user(self.user)
        session.permanent = True
        return self.user


class ForgotPassword(BaseForm):
    email1 = StringField('email', validators=[InputRequired(), Email()])
    email2 = StringField(
        'email (powtórz)', validators=[InputRequired(), Email(), EqualTo('email1')]
    )

    buttons = [
        Button(icon='send', text='wyślij')
    ]

    def save(self):
        user = BrewerProfile.get_by_email(self.email1.data)
        if user is not None and user.email_confirmed:
            payload = {'id': user.id}
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(payload)
            html_body = render_template('email/password_reset.html', token=token)
            sender = current_app.config['EMAIL_SENDER']
            subject = str('Resetowanie hasła w serwisie Brewlog')
            send_email(sender, [user.email], subject, html_body)
            return True
        return False
