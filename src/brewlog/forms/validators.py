import validators
from flask_babel import lazy_gettext as _
from wtforms.validators import ValidationError


class Email:

    def __init__(self, message=None):
        if message is None:
            message = _('Value is not a valid email address')
        self.message = message

    def __call__(self, form, field):
        if not validators.email(field.data):
            raise ValidationError(self.message)


email = Email
