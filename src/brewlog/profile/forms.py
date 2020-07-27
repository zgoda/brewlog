import validators
from wtforms.fields import BooleanField, PasswordField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import EqualTo, InputRequired, ValidationError

from ..ext import db
from ..utils.forms import ActionForm, BaseForm, BaseObjectForm, Button, Link


class ProfileForm(BaseObjectForm):
    first_name = StringField('imię')
    last_name = StringField('nazwisko')
    nick = StringField('pseudo')
    email = EmailField('email', validators=[InputRequired()])
    location = StringField('lokalizacja')
    about_me = TextAreaField('o mnie')
    is_public = BooleanField('profil jest publiczny', default=True)

    def validate_email(self, field):
        if not validators.email(field.data):
            raise ValidationError(f'{field.data} nie jest poprawnym adresem email')

    def save(self, obj):
        return super().save(obj, save=True)

    def validate(self):
        result = super().validate()
        has_name = self.first_name.data and self.last_name.data
        has_nick = self.nick.data
        name_valid = True
        if not (has_name or has_nick):
            name_valid = False
            msg = 'proszę podać imię i nazwisko lub pseudonim'
            self.last_name.errors.append(msg)
            self.first_name.errors.append(msg)
            self.nick.errors.append(msg)
        return result and name_valid


class PasswordChangeForm(BaseForm):
    new_password = PasswordField('nowe hasło', validators=[InputRequired()])
    new_password_r = PasswordField(
        'nowe hasło (powtórz)',
        validators=[EqualTo('new_password'), InputRequired()],
    )

    buttons = [
        Button(text='zapisz'),
        Link(href='javascript:history.back()', text='powrót'),
    ]

    def save(self, user):
        user.set_password(self.new_password.data)
        db.session.add(user)
        db.session.commit()
        return user


class ConfirmBeginForm(ActionForm):

    buttons = [
        Button(text='wyślij', icon='send')
    ]
