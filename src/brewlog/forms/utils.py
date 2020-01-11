from dataclasses import dataclass
from typing import ClassVar

from flask import Markup, render_template_string


class Renderable:

    def render(self):
        return Markup(render_template_string(self.template, obj=self))


@dataclass
class Link(Renderable):
    href: str
    text: str = 'click'

    template: ClassVar[str] = ''.join([
        '<a href="{{ obj.href }}">',
        '{{ obj.text }}',
        '</a>',
    ])


@dataclass
class Button(Renderable):
    type_: str = 'submit'
    class_: str = 'primary'
    icon: str = 'check'
    icon_type: str = 'fas'
    text: str = 'ok'
    link: bool = False

    template: ClassVar[str] = ''.join(
        [
            '<button type="{{ obj.type_ }}" class="btn btn-{{ obj.class_ }}">',
            '<i class="{{ obj.icon_type }} fa-{{ obj.icon }}"></i>',
            '&nbsp;',
            '{{ obj.text }}',
            '</button>',
        ]
    )
