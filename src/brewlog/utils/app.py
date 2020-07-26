from flask import Flask


class Brewlog(Flask):

    def __init__(self, **kwargs):
        return super().__init__('brewlog', **kwargs)

    @property
    def jinja_options(self):
        options = dict(super().jinja_options)
        options.update({
            'trim_blocks': True,
            'lstrip_blocks': True,
        })
        return options
