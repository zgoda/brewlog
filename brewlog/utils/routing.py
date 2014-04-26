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


class RouteCluster(object):

    def __init__(self, endpoint_prefix='', submount='', view_module='', rules=None):
        self._rules = rules or []
        self.endpoint_prefix = endpoint_prefix
        self.submount = submount
        self.view_module = view_module

    def get_rules(self):
        rules = []
        for rule in self._rules:
            url, endpoint, view_name = rule.url, rule.endpoint, rule.view
            extra_kwargs = rule.extra_kwargs
            url = ''.join([self.submount, url])
            endpoint = ''.join([self.endpoint_prefix, endpoint])
            view = '.'.join([self.view_module, view_name])
            rules.append(
                Route(url, endpoint, view, **extra_kwargs)
            )
        return rules


class Route(object):

    def __init__(self, url, endpoint, view, **kwargs):
        self.url = url
        self.endpoint = endpoint
        self.view = view
        self.extra_kwargs = kwargs

    def __repr__(self):  # pragma: no cover
        return '<Route url=%(url)s endpoint=%(endpoint)s view=%(view)s>' % self.__dict__

    def get_rules(self):
        return [self]


class RouteMap(object):

    def __init__(self, root, rules):
        self.root = root
        self._rules = rules

    def get_routes(self):
        rules = []
        for item in self._rules:
            rules.extend(item.get_rules())
        return rules

    def register(self, app):
        for rule in self.get_routes():
            app.add_url_rule(rule.url, rule.endpoint, LazyView('.'.join([self.root, rule.view])), **rule.extra_kwargs)
