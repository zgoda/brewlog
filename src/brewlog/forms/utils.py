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

    template: ClassVar[str] = (
        '<a href="{{ obj.href }}">'
        '{{ obj.text }}'
        '</a>'
    )


@dataclass
class Button(Renderable):
    type_: str = 'submit'
    class_: str = 'primary'
    icon: str = 'check'
    text: str = 'ok'
    iconset: str = 'feather'
    link: bool = False

    template: ClassVar[str] = (
        '<button type="{{ obj.type_ }}" class="button is-{{ obj.class_ }}">'
        '<span class="icon">'
        '<object class="svgicon" data="/static/vendor/{{ obj.iconset }}/{{ obj.icon }}.svg">'  # noqa: E501
        '</object>'
        '</span>'
        '&nbsp;'
        '<span>{{ obj.text }}</spans>'
        '</button>'
    )
