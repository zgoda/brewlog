# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import attr
from flask import Markup, render_template_string


class Renderable:

    def render(self):
        return Markup(render_template_string(self.template, obj=self))


@attr.s
class Link(Renderable):
    href = attr.ib()
    text = attr.ib(default='click')

    template = ''.join([
        '<a href="{{ obj.href }}">',
        '{{ obj.text }}',
        '</a>',
    ])


@attr.s
class Button(Renderable):
    type_ = attr.ib(default='submit')
    class_ = attr.ib(default='primary')
    icon = attr.ib(default='check')
    icon_type = attr.ib(default='fas')
    text = attr.ib('ok')
    link = attr.ib(default=False)

    template = ''.join(
        [
            '<button type="{{ obj.type_ }}" class="btn btn-{{ obj.class_ }}">',
            '<i class="{{ obj.icon_type }} fa-{{ obj.icon }}"></i>',
            '&nbsp;',
            '{{ obj.text }}',
            '</button>',
        ]
    )
