from dataclasses import dataclass
from typing import ClassVar

import validators
from flask import Markup, render_template_string
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms.validators import ValidationError

from ..ext import db


class Renderable:

    def render(self):
        return Markup(render_template_string(self.template, obj=self))


@dataclass
class Link(Renderable):
    href: str
    text: str = 'click'

    template: ClassVar[str] = (
        '<a href="{{ obj.href }}" class="button is-link">'
        '{{ obj.text }}'
        '</a>'
    )


@dataclass
class Button(Renderable):
    type_: str = 'submit'
    class_: str = 'primary'
    icon: str = 'check'
    text: str = 'ok'

    template: ClassVar[str] = (
        '<button type="{{ obj.type_ }}" class="button is-{{ obj.class_ }}">'
        '<span class="icon">'
        '<svg><use xlink:href="#{{ obj.icon }}"></svg>'
        '</span>'
        '&nbsp;'
        '<span>{{ obj.text }}</spans>'
        '</button>'
    )


class BaseForm(FlaskForm):
    pass


class BaseObjectForm(BaseForm):

    buttons = [
        Button(text=_('save')),
        Link(href='javascript:history.back()', text=_('go back')),
    ]

    def save(self, obj, save=False):
        self.populate_obj(obj)
        if save:
            db.session.add(obj)
            db.session.commit()
        return obj


class DeleteForm(BaseForm):
    delete_it = BooleanField(_('delete'), default=False)

    buttons = [
        Button(text=_('confirm')),
    ]


class ActionForm(BaseForm):

    buttons = [
        Button(text=_('confirm')),
    ]


class Email:

    def __init__(self, message=None):
        if message is None:
            message = _('Value is not a valid email address')
        self.message = message

    def __call__(self, form, field):
        if not validators.email(field.data):
            raise ValidationError(self.message)


email = Email
