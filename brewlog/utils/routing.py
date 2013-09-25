from werkzeug import import_string, cached_property


class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


class Rule(object):

    def __init__(self, url, rule_args):
        self.url = url
        self.rule_args = rule_args
        self.rule_args['view_func'] = LazyView(rule_args['view_func'])


class UrlMap(object):

    def __init__(self, rules):
        self.rules = rules

    def register(self, app):
        for rule in self.rules:
            app.add_url_rule(rule.url, **rule.rule_args)
